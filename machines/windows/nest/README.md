---
machine: Nest
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, smb, encrypted-config, vb-net, alternate-data-stream, hqk, psexec]
---

# Nest — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SMB anónimo expone una bienvenida con credenciales de `TempUser`. Con esa cuenta se accede a `Secure$` y a un XML con la contraseña cifrada de `c.smith`; el proyecto Visual Basic del propio escáner incluye el código de descifrado. `c.smith` lee su flag y encuentra una contraseña de depuración en un flujo alternativo de NTFS. El servicio HQK filtra la contraseña cifrada del administrador y el binario `HqkLdap.exe` permite descifrarla; `psexec` da SYSTEM.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p445,4386 <IP>
```

- SMB en 445.
- Servicio personalizado `HQK Reporting Service V1.2` en 4386.
- El puerto 4386 responde a `HELP`, `LIST`, `SETDIR`, `RUNQUERY` y `DEBUG`.

## Enumeración

```bash
smbclient -N -L //<IP>/
smbclient -N //<IP>/Data
smbclient -N //<IP>/Users
```

`Data` contiene `Welcome Email.txt` con las credenciales `TempUser` / `<TEMP_PASSWORD>`. `Users` permite listar nombres, pero no leer sus carpetas.

Con `TempUser` se accede a `Secure$` y se descargan los configs de IT:

```bash
smbclient -U 'TempUser%<TEMP_PASSWORD>' //<IP>/Secure$
recurse on
prompt off
mget *
```

`IT/Configs/RU Scanner/RU_config.xml` contiene el usuario `c.smith` y una contraseña cifrada `<CIPHER>`. El proyecto `RUScanner` incluye `Utils.vb` con `DecryptString`; ejecutándolo se obtiene `<CSMITH_PASSWORD>`.

## Foothold

```bash
smbclient -U 'c.smith%<CSMITH_PASSWORD>' //<IP>/Users
```

Se lee `C.Smith/user.txt` y se descarga `HQK Reporting`. El archivo `Debug Mode Password.txt` parece vacío, pero `allinfo` muestra un flujo alternativo `:Password:$DATA`.

```bash
allinfo "Debug Mode Password.txt"
get "Debug Mode Password.txt:Password"
```

El contenido es la contraseña de depuración `<DEBUG_PASSWORD>`.

## Escalada de privilegios

Se conecta al servicio HQK y se activa el modo debug:

```bash
telnet <IP> 4386
DEBUG <DEBUG_PASSWORD>
SHOWQUERY 2
```

La consulta incluye `ldap.conf` con el usuario `Administrator` y otra contraseña cifrada. `HqkLdap.exe` es el módulo que descifra; ejecutándolo con el archivo como argumento y un breakpoint después de la llamada de descifrado se obtiene `<ADMIN_PASSWORD>`.

```bash
psexec.py administrator:'<ADMIN_PASSWORD>'@<IP>
```

La shell es `NT AUTHORITY\SYSTEM`; se lee `root.txt`.

## Evidencia

- `smbclient` con credenciales redactadas.
- `RU_config.xml` y `allinfo` del ADS.
- `SHOWQUERY` con la contraseña cifrada.
- `psexec` y `whoami` como SYSTEM.

## Lecciones aprendidas

- Los shares anónimos pueden encadenar credenciales de forma incremental.
- Un proyecto de Visual Basic entregado al cliente puede incluir la rutina de descifrado.
- Los flujos alternativos de NTFS ocultan datos que `dir` no muestra.
- Un servicio de reporting puede filtrar configuraciones LDAP.

## Mitigaciones y detección

- Deshabilitar SMB anónimo y revisar permisos de `Data` y `Secure$`.
- No almacenar contraseñas cifradas con claves embebidas en el cliente.
- Auditar flujos alternativos y borrar secretos de archivos de depuración.
- Restringir HQK a administradores y no devolver configuraciones completas.
- Alertar de `psexec`, servicios creados y lectura de `:Password:$DATA`.

## Referencias

- <https://www.hackthebox.com/machines/Nest>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://attack.mitre.org/techniques/T1564/004/>
- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/c54dec26-1551-4d3a-a0ea-4fa40f848eb3>
