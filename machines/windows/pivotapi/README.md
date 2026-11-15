---
machine: PivotAPI
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, mssql, reversing, laps, asrep]
---

# PivotAPI — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un PDF en FTP anónimo filtra un nombre de usuario; AS-REP Roasting da la primera cuenta. El reversing de un binario ofuscado revela credenciales de MSSQL, que se usa como túnel hacia WinRM. Una cadena de ACL y LAPS cierra el dominio.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,80,1433,3389,5985 <IP>
ftp <IP>
exiftool document.pdf | grep -i author
GetNPUsers.py <DOMAIN>/ -usersfile users.txt -no-pass -dc-ip <DC>
# Reversing
ilspycmd app.exe > app.cs
# MSSQL
mssqlclient.py <USER>@<IP> -windows-auth
bloodhound-python -u <USER> -p "<PASS>" -d <DOMAIN> -c All
```

## Enumeración

- FTP anónimo con documentos y metadatos.
- Usuarios sin preautenticación Kerberos y MSSQL expuesto.
- Binario ofuscado con credenciales y permisos de LAPS en AD.

## Acceso inicial

`exiftool` sobre el PDF revela un usuario. `GetNPUsers.py` obtiene un AS-REP crackeable y la contraseña permite entrar al portal. El binario se analiza con Procmon/ILSpy y se recuperan credenciales de MSSQL.

## Escalada de privilegios

MSSQL se usa como pivote para ejecutar comandos y llegar a WinRM. BloodHound muestra permisos para leer LAPS; se recupera la contraseña local del administrador y se usa para DCSync o acceso al DC.

## Evidencia

- Metadatos del PDF con el usuario.
- AS-REP crackeado y acceso inicial.
- Consulta MSSQL, túnel WinRM y contraseña LAPS.

## Lecciones aprendidas

- Los metadatos de documentos filtran cuentas.
- MSSQL puede ser un pivote y una vía de ejecución.
- Los permisos de lectura de LAPS son equivalentes a credenciales locales.

## Mitigación y detección

- Limpiar metadatos y restringir FTP anónimo.
- Exigir preautenticación Kerberos y limitar MSSQL.
- Auditar quién puede leer LAPS y aplicar mínimo privilegio.

## Referencias

- [0xdf — PivotAPI](https://0xdf.gitlab.io/2021/11/06/htb-pivotapi.html)
- [Microsoft — LAPS](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview)
- [Hack The Box — PivotAPI](https://app.hackthebox.com/machines/pivotapi)
