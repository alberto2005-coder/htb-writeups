---
machine: Usage
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, laravel, blind-sqli, laravel-admin, webshell, monit, wildcard, 7z, privesc]
---

# Usage — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Password reset is blind SQLi; dump the database and get the admin login. Laravel-Admin allows a webshell upload by changing the extension after client-side validation, giving `dash`. A `.monitrc` password works for `xander`, who can run `usage_management` as root; the script uses `7za` with a wildcard, and an `@list` file plus a symlink read root's SSH key.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nginx with a Laravel site.
- `ffuf` finds `usage.htb` and `admin.usage.htb`.
- The error page is Laravel's and cookies are `laravel_session`.

## Enumeration

- The password reset form is blind SQLi.
- `sqlmap` dumps the database and recovers the admin user and hash.
- The `admin.usage.htb` panel uses Laravel-Admin.

```bash
sqlmap -r reset.req --batch --dbs
```

## Foothold

Laravel-Admin validates the extension client-side but not server-side. Upload a `.php` image by changing the extension after validation and visit the avatar path to run the webshell as `dash`.

```text
POST /admin/profile/avatar
filename=shell.php
```

## Lateral movement

`dash`'s `.monitrc` contains a password. It works for `xander` with `su` and over SSH.

```bash
cat ~/.monitrc
su - xander
```

## Privilege escalation

`xander` can run `/usr/bin/usage_management` as root. Option 1 runs:

```bash
/usr/bin/7za a /var/backups/project.zip -tzip -snl -mmt -- *
```

Create `@0xdf` and a symlink `0xdf` to `/root/.ssh/id_rsa`. `7za` treats `@0xdf` as a file list and prints the symlink contents in errors, leaking root's key.

```bash
touch @0xdf; ln -fs /root/.ssh/id_rsa 0xdf
sudo usage_management
```

## Evidence

- Blind SQLi in reset.
- Laravel-Admin and webshell as `dash`.
- `.monitrc` and `xander`.
- `7za` wildcard and root SSH key.

## Lessons learned

- Client-side extension validation does not protect uploads.
- Blind SQLi can dump the whole database.
- Monit configuration files store credentials.
- A `7z` wildcard with an `@list` leaks files.

## Mitigation and detection

- Validate type and extension server-side and rename files.
- Parameterize queries and rate-limit reset.
- Protect `.monitrc` and never reuse its password.
- Avoid wildcards; use `find`/`-print0` and absolute paths.

## References

- [0xdf — Usage](https://0xdf.gitlab.io/2024/08/10/htb-usage.html)
- [IppSec — Usage](https://www.youtube.com/watch?v=cx9Da-PoXG4)
- [Hack The Box — Usage](https://app.hackthebox.com/machines/usage)
