---
machine: Phoenix
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, wordpress, sqli, totp, wildcard]
---

# Phoenix — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

WordPress 5.9 with Asgaros Forum 1.15.35 is vulnerable to time-based SQLi (CVE-2021-24827). Extract `phoenix`'s hash, crack it and access the panel, where the `download-from-files` plugin allows uploading PHP. TOTP is bypassed by a PAM rule trusting `10.11.12.13`, and a wildcard `rsync` run by cron gives root.

## Recon

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- `22/tcp` OpenSSH, `80/tcp` redirects to `https://phoenix.htb` and `443/tcp` serves WordPress.
- `wpscan` identifies WordPress 5.9, the `phoenix` theme and Asgaros Forum 1.15.35.
- The certificate and vhost confirm `phoenix.htb`.

## Enumeration

- The forum exposes `forum.php` and the topic `id` parameter.
- The Asgaros version is vulnerable to time-based SQLi in `orderby`/`order`.
- `wpscan --enumerate u` lists `phoenix`; the hash is in `wp_users`.

## Foothold

Confirm SQLi with `SLEEP(5)` and extract `phoenix`'s hash with `sqlmap`. After cracking it, log in to WordPress and install the `download-from-files` plugin, which uploads and executes PHP.

```bash
sqlmap -u 'https://phoenix.htb/forum/?id=1' --batch --dbs
hashcat -m 400 hash.txt rockyou.txt
# Dashboard -> Plugins -> download-from-files -> upload shell.php
```

## Lateral movement

The shell lands as `www-data`. The WordPress database contains the user's TOTP seed and the PAM configuration lives in `/etc/pam.d/`; read it as `phoenix` after recovering the password.

## Privilege escalation

`phoenix` has TOTP, but `/etc/pam.d/access-local.conf` allows `pam_access` without OTP from `10.11.12.13`. Add that IP to loopback and use `su phoenix`. `sudo -l` shows a script running `rsync` with a wildcard; create a file named `--rsh=...` to force `-e bash` and execute as root.

```bash
sudo -l
# /usr/bin/rsync -a /home/phoenix/ /opt/backups/
touch -- '--rsh=bash'
```

## Evidence

- Delayed response from `SLEEP(5)` in Asgaros.
- Cracked `phoenix` hash and malicious plugin installed.
- `access-local.conf` and a `--rsh=bash` file in the backup directory.

## Lessons learned

- A WordPress plugin with file upload is remote execution once the panel is reached.
- IP-based PAM rules can nullify a second factor.
- Wildcards in privileged scripts allow injecting options such as `--rsh`.

## Mitigation and detection

- Update Asgaros and WordPress; remove unmaintained plugins.
- Do not trust source IP to skip MFA; require TOTP consistently.
- Avoid wildcards with `rsync`/`tar` and use `--` plus explicit file lists.

## References

- [0xdf — Phoenix](https://0xdf.gitlab.io/2022/06/25/htb-phoenix.html)
- [IppSec — Phoenix](https://www.youtube.com/watch?v=Zngo-QzZYtw)
- [Hack The Box — Phoenix](https://app.hackthebox.com/machines/phoenix)
