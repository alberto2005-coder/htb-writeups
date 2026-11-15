---
topic: Pivoting with MSSQL linked servers
tags: [windows, mssql, linked-server, xp_cmdshell, pivot]
---

# Pivoting with MSSQL linked servers

[🌐 Español](mssql-linked-server-pivot.md) | **English**

## Concept

An MSSQL server can have linked servers to other hosts. If the remote login mapping is `sysadmin`, a low-privilege account on the first server can run queries and commands on the second.

## When it applies

- MSSQL access with a valid user is available.
- `enum_links` shows a linked server.
- The remote mapping has high privileges.

## Procedure

1. Enumerate linked servers and mappings.
2. Test `SELECT SYSTEM_USER` on the remote server.
3. Enable `xp_cmdshell` if needed.
4. Run commands and obtain a shell.

```sql
enum_links
EXEC ('SELECT SYSTEM_USER') AT [DC02.darkzero.ext]
use_link [DC02.darkzero.ext]
enable_xp_cmdshell
xp_cmdshell whoami
```

## Variants

- Use `OPENQUERY` for remote queries.
- Abuse `sp_configure` to enable commands.
- Chain to a third server.

## Limitations

- The linked server must be configured.
- The remote login must have permissions.
- `xp_cmdshell` may be disabled.

## Mitigation and detection

- Remove unnecessary linked servers.
- Avoid `sysadmin` mappings and use least-privilege accounts.
- Disable and audit `xp_cmdshell`.

## References

- <https://learn.microsoft.com/en-us/sql/relational-databases/linked-servers/linked-servers-database-engine>
- <https://github.com/fortra/impacket>
- <https://attack.mitre.org/techniques/T1210/>
