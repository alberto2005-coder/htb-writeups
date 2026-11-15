---
machine: Breadcrumbs
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, php, jwt, sqlite, sqli, aes]
---

# Breadcrumbs — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A PHP traversal reads the source and allows forging the session/JWT cookie for admin access. Sticky Notes and a SQLite database with WAL/SHM lead to another user; a UNION SQLi and the AES key reach administrator.

## Reconnaissance

```bash
nmap -Pn -sCV -p80,445,3389,5985 <IP>
gobuster dir -u http://breadcrumbs.htb -w /usr/share/wordlists/dirb/common.txt
# Traversal and cookie forgery
curl -s "http://breadcrumbs.htb/download.php?file=../../../../var/www/html/index.php"
# SQLite with WAL/SHM
cp StickyNotes.snt StickyNotes.snt-wal StickyNotes.snt-shm /tmp/
sqlite3 /tmp/StickyNotes.snt ".tables"
# UNION SQLi
sqlmap -u "http://breadcrumbs.htb/portal.php" --data="search=test" --batch --dump
```

## Enumeration

- PHP application with file parameters and session cookies.
- Sticky Notes and a SQLite database with `-wal` and `-shm` files.
- Password manager with a SQLi query.

## Initial access

The traversal reads the source and reveals how the session is signed. Forge an administrator cookie, upload a webshell and obtain execution on IIS.

## Privilege escalation

Sticky Notes stores another user's credentials. Copy the SQLite database with its WAL/SHM files to recover uncommitted data; a UNION SQLi in the manager extracts the encrypted material and AES key, which decrypts and grants administrator access.

## Evidence

- PHP source read through traversal.
- Forged admin cookie and webshell.
- SQLite with WAL/SHM and decrypted AES secret.

## Lessons learned

- WAL/SHM files contain data not present in the main database.
- A cookie signed with a leaked secret is a direct door.
- SQLi can expose keys that protect other secrets.

## Mitigation and detection

- Do not embed signing secrets in accessible code.
- Encrypt and protect Sticky Notes and manager databases.
- Parameterize queries and delete SQLite temporary files.

## References

- [0xdf — Breadcrumbs](https://0xdf.gitlab.io/2021/07/17/htb-breadcrumbs.html)
- [SQLite — WAL format](https://www.sqlite.org/wal.html)
- [Hack The Box — Breadcrumbs](https://app.hackthebox.com/machines/breadcrumbs)
