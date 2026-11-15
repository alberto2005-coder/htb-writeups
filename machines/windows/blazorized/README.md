---
machine: Blazorized
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, blazor, jwt, sqli, kerberoasting, dcsync]
---

# Blazorized — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una DLL de Blazor WebAssembly filtra el secreto de firma JWT; se forja un token de administrador y se explota SQLi con `xp_cmdshell`. Después, `WriteSPN` permite targeted Kerberoasting y la cadena de ACL lleva a DCSync.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,445,3389,5985 <IP>
wget -q http://blazorized.htb/_framework/Blazorized.Client.dll -O client.dll
strings -el client.dll | grep -iE "secret|key|jwt"
python3 jwt_tool.py <TOKEN> -S hs256 -p "<SECRETO>"
sqlmap --url "http://blazorized.htb/api/..." --os-shell
# AD
bloodhound-python -u <USER> -p "<PASS>" -d blazorized.htb -c All
targetedKerberoast.py -d blazorized.htb -u <USER> -p "<PASS>"
```

## Enumeración

- Aplicación Blazor con DLL descargables y panel administrativo.
- JWT con algoritmo HMAC y un secreto embebido en el cliente.
- SQL Server accesible desde el panel y usuarios de AD con SPN escribible.

## Acceso inicial

Se descarga `Blazorized.Client.dll` y se buscan cadenas que parezcan claves. Con el secreto se firma un JWT con rol de administrador; el panel permite SQLi y `xp_cmdshell` da una shell en el host.

## Escalada de privilegios

BloodHound muestra `WriteSPN` sobre una cuenta. Se escribe un SPN, se hace targeted Kerberoasting, se crackea el hash y se obtiene otro usuario. Un script de inicio modificable y permisos de replicación permiten DCSync.

## Evidencia

- Secreto JWT recuperado de la DLL.
- Token de admin aceptado por la API.
- Consulta SQLi y `whoami` vía `xp_cmdshell`.

## Lecciones aprendidas

- El secreto de firma nunca debe llegar al cliente.
- Un SPN escribible convierte una cuenta en objetivo de Kerberoasting.
- Las ACL encadenadas permiten escalar sin exploits de memoria.

## Mitigación y detección

- Validar JWT en el servidor y rotar el secreto.
- Restringir `WriteSPN` y usar cuentas de servicio gestionadas.
- Auditar scripts de inicio y permisos de replicación.

## Referencias

- [0xdf — Blazorized](https://0xdf.gitlab.io/2024/11/09/htb-blazorized.html)
- [Microsoft — JWT validation](https://learn.microsoft.com/en-us/entra/identity-platform/security-tokens)
- [Hack The Box — Blazorized](https://app.hackthebox.com/machines/blazorized)
