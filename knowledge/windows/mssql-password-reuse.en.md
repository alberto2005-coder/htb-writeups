---
topic: MSSQL — password reuse and RBCD
tags: [windows, mssql, password-spray, rbcd, activedirectory]
---

# MSSQL — password reuse and RBCD

[🇪🇸 Español](mssql-password-reuse.md) | **English**

## Concept

MSSQL often shares credentials with domain and local accounts. SQLi or database access yields a service user; `xp_cmdshell` gives execution, a spray finds accounts with the same password, and one may have rights to configure RBCD.

## When it applies

- MSSQL credentials or SQLi in an application are available.
- `xp_cmdshell` is enabled or can be enabled.
- The password is reused on AD accounts.

## Procedure

1. Authenticate to MSSQL and enumerate users and permissions.
2. Enable `xp_cmdshell` and get a shell.
3. Extract configuration credentials and spray.
4. Look for write rights over computers and configure RBCD.

```bash
impacket-mssqlclient <DOMAIN>/<USER>:'<PASSWORD>'@<IP> -windows-auth
EXEC sp_configure 'show advanced options',1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;
```

```bash
netexec smb <DC> -u users.txt -p passwords.txt -d <DOMAIN>
```

## Variants

- `xp_dirtree` to read backups without `xp_cmdshell`.
- `RunasCs` to use local credentials.
- `SeImpersonate` for a potato when RBCD is unavailable.

## Limitations

- `xp_cmdshell` may be disabled without rights to change it.
- Sprays lock accounts under a lockout policy.
- RBCD needs a controlled computer and write rights.

## Mitigation

- Unique passwords and LAPS; no reuse on services.
- Restrict `xp_cmdshell` and database permissions.
- Audit `msDS-AllowedToActOnBehalfOfOtherIdentity`.

## Detection

- `xp_cmdshell` and child processes of SQL Server.
- Distributed logins with the same password.
- RBCD writes on computer objects.

## References

- [0xdf — Freelancer](https://0xdf.gitlab.io/2024/10/05/htb-freelancer.html)
- [Microsoft — xp_cmdshell](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/xp-cmdshell-transact-sql)
- [MITRE ATT&CK — T1110](https://attack.mitre.org/techniques/T1110/)
