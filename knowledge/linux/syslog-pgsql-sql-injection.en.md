---
topic: rsyslog to PostgreSQL — SQL injection in templates
tags: [linux, rsyslog, postgresql, sqli, privesc]
---

# rsyslog to PostgreSQL — SQL injection in templates

[🇪🇸 Español](syslog-pgsql-sql-injection.md) | **English**

## Concept

rsyslog's `ompgsql` module sends every message to PostgreSQL using a template. If the template concatenates the message without parameterization, log content becomes SQL. With `logger -p local7.info`, any user who can write to that facility controls the query; stacked queries and `COPY ... TO` read and write files as `postgres`.

## When it applies

- rsyslog forwards logs to PostgreSQL with an `sql-syslog` template.
- The user can write to the configured facility (`local7.info`).
- PostgreSQL accepts stacked queries and the user has file permissions.

## Procedure

1. Read `/etc/rsyslog.d/*.conf` and locate the template and facility.
2. Send a message with `'` and inspect `/var/log/postgresql`.
3. Close the string with `', null)-- -` and test `;`.
4. Use `COPY ... TO` or `FROM PROGRAM` to execute or write.

```bash
logger -p local7.info "test', null)-- -"
logger -p local7.info "x',null); CREATE TABLE aaa (c text);-- -"
```

```bash
logger -p local7.info "x',null); COPY (SELECT '') TO \\$$/tmp/pwned\\$$;-- -"
```

## Variants

- `COPY ... FROM PROGRAM` for direct execution.
- Write `postgres`'s `authorized_keys` from a temporary table.
- Read `.psql_history` for credentials and reuse them.

## Limitations

- rsyslog escapes `'` with `\`, so the syntax needs adjustment.
- The PostgreSQL user may not be a superuser.
- `COPY ... PROGRAM` requires permissions and a writable path.

## Mitigation

- Parameterize the template or use JSON and a staging table.
- Restrict `pg_execute_server_program` and file `COPY`.
- Separate the log facility from untrusted users.

## Detection

- SQL syntax errors in PostgreSQL logs.
- `COPY ... PROGRAM` or `COPY ... TO` in ` STATEMENT`.
- `logger` messages containing quotes and SQL comments.

## References

- [rsyslog — ompgsql](https://www.rsyslog.com/doc/configuration/modules/ompgsql.html)
- [0xdf — Zetta](https://0xdf.gitlab.io/2020/02/22/htb-zetta.html)
- [PostgreSQL — COPY](https://www.postgresql.org/docs/current/sql-copy.html)
