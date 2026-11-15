---
machine: Surveillance
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, craftcms, zoneminder, cve, privesc]
---

# Surveillance — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Craft CMS 4.4.14 is vulnerable to CVE-2023-41892 and allows unauthenticated code execution. A SQL backup exposes `matthew`'s SHA-256 hash, cracked to log in over SSH. ZoneMinder 1.36.32 has CVE-2023-26035 and an update script run with `sudo` that allows command injection.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 22.04 and `80/tcp` nginx serving `surveillance.htb`.
- The site uses Craft CMS and redirects to `/admin` for the panel.
- The footer and `/admin/login` confirm Craft CMS 4.4.14.

## Enumeration

- `CVE-2023-41892` abuses `conditions` in a request to `actions/conditions/render` to instantiate objects and run PHP.
- The public exploit drops a webshell in `/tmp` or runs commands directly.
- The system contains a `backup.sql` with Craft's user table.

## Foothold

Use the Craft exploit to run a reverse shell as `www-data`. Then locate `backup.sql`, extract `matthew`'s SHA-256 hash and crack it with `hashcat -m 1400`.

```bash
python3 CVE-2023-41892.py http://<IP>
# shell as www-data
find / -name backup.sql 2>/dev/null
hashcat -m 1400 hash.txt rockyou.txt
ssh matthew@<IP>
```

## Lateral movement

`matthew` has SSH access and can enumerate local services. ZoneMinder listens on `localhost:8080`; its credentials and system configuration are reachable from the user.

## Privilege escalation

`sudo -l` allows `/usr/bin/zm*.pl` as root. ZoneMinder 1.36.32 is vulnerable to CVE-2023-26035 and its `zmupdate.pl` script passes parameters to a shell; inject a command or use `LD_PRELOAD` with a custom library to run code as root.

```bash
sudo -l
sudo /usr/bin/zmupdate.pl --user='; /bin/bash #'
# Alternative: sudo LD_PRELOAD=/tmp/pwn.so /usr/bin/zmupdate.pl
```

## Evidence

- Unauthenticated PHP execution in Craft CMS.
- Cracked SHA-256 hash for `matthew`.
- `sudo -l` with `zm*.pl` and a root shell.

## Lessons learned

- An outdated CMS can provide unauthenticated execution.
- Database backups often contain crackable hashes.
- A `sudo` maintenance script with unsanitized parameters is root execution.

## Mitigation and detection

- Update Craft CMS and ZoneMinder to fixed versions.
- Restrict and encrypt backups; never leave them in the webroot.
- Avoid `sudo` on scripts accepting parameters and keep `env_reset` enabled.

## References

- [0xdf — Surveillance](https://0xdf.gitlab.io/2024/04/20/htb-surveillance.html)
- [IppSec — Surveillance](https://www.youtube.com/watch?v=HMC5WZH3o-E)
- [Hack The Box — Surveillance](https://app.hackthebox.com/machines/surveillance)
