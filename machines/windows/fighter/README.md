---
machine: Fighter
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, iis, sqli, xp-cmdshell, applocker, msbuild, capcom, privesc]
---

# Fighter — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web de IIS tiene una SQLi apilada que permite habilitar `xp_cmdshell` y ejecutar comandos como `sqlserv`; una reverse shell de PowerShell da acceso. `clean.bat`, ejecutado por una tarea programada de `decoder`, es escribible: se trunca y se reescribe para obtener esa cuenta. El driver `Capcom.sys` cargado en el sistema permite ejecutar código en modo kernel y alcanzar SYSTEM. Como alternativa, AppLocker se puede saltar con `MSBuild.exe` y un XML con `UsingTask`.

## Reconocimiento

```bash
nmap -Pn -sCV -p80 <IP>
```

- `80` IIS 8.5 con una web temática de Street Fighter y varios vhosts.
- MSSQL 2014 está detrás de la web; no hay SMB ni RDP expuestos.
- Windows Server 2012 R2, sin parches recientes que sirvan como vector.

## Enumeración

`wfuzz` descubre vhosts y `feroxbuster` rutas de la aplicación. El formulario de login es vulnerable a inyección SQL; una consulta apilada permite ejecutar `EXEC xp_cmdshell 'whoami'` y confirma que la base corre como `sqlserv`.

## Foothold

La SQLi apilada permite `xp_cmdshell`; se usa para lanzar PowerShell y obtener una reverse shell como `sqlserv`. En Beyond Root, AppLocker se evade con `MSBuild.exe`, un ejecutable de confianza que compila una tarea `UsingTask` con `TaskFactory="CodeTaskFactory"` y ejecuta C# en memoria. La variante es:

```powershell
C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe sc.xml
```

## Movimiento lateral

`C:\users\decoder\clean.bat` tiene permiso de modificación para `Everyone`. No se puede sobrescribir directamente, pero `cmd /c copy /y NUL clean.bat` lo deja vacío y después se añade el payload. La tarea programada de `decoder` lo ejecuta, dando una shell como ese usuario.

## Escalada de privilegios

`driverquery /v` muestra `Capcom.sys`, un driver firmado y vulnerable que permite escribir en memoria del kernel desde modo usuario. Se usa un exploit público para deshabilitar las protecciones y ejecutar una shell como SYSTEM.

```powershell
driverquery /v | findstr /iv "system32\\drivers"
sc.exe query capcom
```

## Evidencia

- `xp_cmdshell` ejecutando `whoami` como `sqlserv`.
- `MSBuild.exe` con el XML de tarea como bypass alternativo.
- `clean.bat` truncado y reescrito.
- Driver `Capcom.sys` y shell de SYSTEM.

## Lecciones aprendidas

- AppLocker basado en rutas y extensiones deja pasar binarios firmados.
- Los scripts de tareas programadas con permisos amplios son un salto de usuario.
- Un driver firmado vulnerable rompe por completo el límite kernel/usuario.
- Enumerar drivers es tan importante como enumerar servicios.

## Mitigación y detección

- Parametrizar las consultas y deshabilitar `xp_cmdshell`.
- Aplicar AppLocker/WDAC con reglas de publisher y bloquear MSBuild para usuarios no desarrolladores.
- Restringir ACLs de scripts ejecutados por tareas programadas.
- Usar HVCI y bloquear drivers vulnerables conocidos (Capcom.sys).

## Referencias

- [0xdf — Fighter](https://0xdf.gitlab.io/2022/04/25/htb-fighter.html)
- [IppSec — Fighter](https://www.youtube.com/watch?v=CW4mI5BkP9E)
- [Hack The Box — Fighter](https://app.hackthebox.com/machines/fighter)
