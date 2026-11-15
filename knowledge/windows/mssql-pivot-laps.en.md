---
topic: MSSQL — pivot, execution and LAPS
tags: [windows, mssql, pivot, active-directory, laps]
---

# MSSQL — pivot, execution and LAPS

**English** | [🌐 Español](mssql-pivot-laps.md)

## Concept

MSSQL with user credentials allows queries, file reads and, with `xp_cmdshell` or `EXECUTE AS`, command execution. It also pivots to other hosts. In Active Directory, permissions to read LAPS expose the local administrator password, reused for lateral movement and DCSync.

## When it applies

- MSSQL is exposed and credentials are available.
- The user has execution rights or `sysadmin`.
- BloodHound shows rights over LAPS-enabled objects.

## Procedure

1. Connect with `mssqlclient.py` and enumerate privileges.
2. Run commands or queries to move to the next host.
3. Enumerate AD and find LAPS read permissions.
4. Recover the password and use it for DCSync.

## Commands

```bash
mssqlclient.py <USER>@<HOST> -windows-auth
SQL> enable_xp_cmdshell
SQL> xp_cmdshell whoami
bloodhound-python -u <USER> -p "<PASS>" -d <DOMAIN> -c All
# LAPS read
Get-ADComputer -Filter * -Properties ms-Mcs-AdmPwd | select Name,ms-Mcs-AdmPwd
```

## Variants

- Use `EXECUTE AS LOGIN` to change context.
- Read files with `OPENROWSET`.
- Use `certipy` or `secretsdump` after obtaining the LAPS password.

## Limitations

- The user may lack `sysadmin`.
- LAPS may be migrated to Windows LAPS with another attribute.
- The firewall may limit the pivot.

## Mitigation

- Enforce least privilege in MSSQL and disable `xp_cmdshell`.
- Audit who can read LAPS.
- Segment the network and rotate local passwords.

## Detection

- Queries against `ms-Mcs-AdmPwd`.
- `xp_cmdshell` and SQL Server child processes.
- Lateral authentication with computer accounts.

## References

- [0xdf — PivotAPI](https://0xdf.gitlab.io/2021/11/06/htb-pivotapi.html)
- [Microsoft — LAPS](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
