---
machine: Nocturnal
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, idor, command-injection, ispconfig, sqlite]
---

# Nocturnal — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`view.php` serves files by name without checking ownership and allows downloading another user's backup. The admin panel runs a backup with a controllable parameter; newlines and tabs bypass the filter and yield a shell. The SQLite database holds `tobias`'s MD5 hash, and the ISPConfig panel is vulnerable to CVE-2023-46818, leading to root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 22.04 and `80/tcp` nginx serving `nocturnal.htb`.
- The site allows registration, file upload and viewing through `view.php?filename=`.
- `admin.nocturnal.htb` hosts an administration panel with a login.

## Enumeration

- `view.php` does not validate ownership: other users' files can be requested.
- Backups are stored as `<user>_<timestamp>.zip` and downloaded from the same route.
- The administrator backup contains the SQLite database with users and MD5 hashes.

## Foothold

Download the other user's backup and extract the database. Crack `tobias`'s hash and use it to access the admin panel. The backup function concatenates the filename into a command; inject with `%0a` and tabs to evade the filter.

```bash
curl 'http://nocturnal.htb/view.php?filename=<ADMIN>_<TS>.zip' -o admin.zip
unzip admin.zip
hashcat -m 0 hash.txt rockyou.txt
# In the panel: backup name with a newline and a tab
```

## Lateral movement

The shell lands as `www-data`. The database and configuration files allow pivoting to `tobias` over SSH; his password is reused on the ISPConfig panel.

## Privilege escalation

ISPConfig 3.2.11 is vulnerable to CVE-2023-46818: the `language_file` parameter in the language editor includes a PHP file and runs code as the panel user, which is root.

```bash
python3 cve-2023-46818.py http://localhost:8080 <USER> <PASSWORD>
# The exploit writes a PHP file and invokes it from the language editor
```

## Evidence

- Another user's backup downloaded through `view.php`.
- Cracked MD5 hash and admin panel access.
- `www-data` shell and root execution through ISPConfig.

## Lessons learned

- A file identifier must enforce ownership server-side.
- Blacklist-based command filters are bypassed with newlines.
- A root-running hosting panel with a recent CVE compromises the whole host.

## Mitigation and detection

- Use IDs and verify the resource belongs to the authenticated user.
- Run backups with `execve` and separate arguments, never through a shell.
- Keep ISPConfig patched and restrict it to the internal network.

## References

- [0xdf — Nocturnal](https://0xdf.gitlab.io/2025/08/16/htb-nocturnal.html)
- [IppSec — Nocturnal](https://www.youtube.com/watch?v=tjA3sXsnPqw)
- [Hack The Box — Nocturnal](https://app.hackthebox.com/machines/nocturnal)
