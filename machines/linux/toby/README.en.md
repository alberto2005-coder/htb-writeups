---
machine: Toby
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, php, backdoor, mysql, gogs, pam, privesc]
---

# Toby — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Toby follows a previous attacker: an obfuscated PHP webshell loads from the WordPress theme and communicates through a specific parameter. From there, pivot to a MySQL container, crack hashes and enter Gogs. Source code and a password generator move to the host as `jack`; a PAM backdoor with a ten-character password is found in a ticket and brute-forced by timing to root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nginx with WordPress and a `gogs.toby.htb` vhost.
- `wpscan` enumerates plugins and themes; the active theme has a suspicious PHP file.
- `gobuster` finds `/wp-content/themes/<THEME>/`.

## Enumeration

- The theme includes an obfuscated webshell; the code expects a parameter and a key.
- Deobfuscate it with CyberChef or `php -r` and identify the execution parameter.
- The webshell talks to an internal MySQL container.

```bash
curl 'http://toby.htb/wp-content/themes/<THEME>/<FILE>.php?<PARAM>=id'
```

## Foothold

Use the webshell to run a reverse shell as `www-data`. Enumeration shows a MySQL container and credentials in the WordPress configuration.

```bash
mysqldump -u <USER> -p'<PASSWORD>' --all-databases > /tmp/db.sql
```

## Lateral movement

The database holds Gogs and system user hashes. Crack them and access Gogs as `toby-admin`; the `supportsystem-db` repository includes a password generator and support code. The generator produces a wordlist and cracks `jack`'s hash; the password works on the MySQL container and over SSH to the host.

```bash
hashcat -m 11200 jack.hash passwordlist
ssh jack@toby.htb
```

## Privilege escalation

The support ticket mentions a modified PAM module. In `/lib/security` a `.so` has an anomalous date; Ghidra shows it compares a ten-character password with a comparison that takes longer as the matching prefix grows. A script measures `su` timing and recovers the password character by character; it logs in as root.

```bash
for c in 0 1 2 3 4 5 6 7 8 9; do printf '%s' "$candidate$c" | timeout 2 su -c true root; done
```

## Evidence

- Obfuscated theme webshell and secret parameter.
- MySQL container and hashes.
- Gogs, password generator and `jack`.
- PAM module with a ten-character password.
- Timing attack and root.

## Lessons learned

- A WordPress theme can hide a webshell that only answers a specific parameter.
- Internal containers widen the surface and leak databases.
- A password generator in a repository reduces the search space.
- A non-constant PAM comparison leaks the password through timing.

## Mitigation and detection

- Audit themes and plugins; compare files with upstream.
- Isolate containers and do not reuse credentials across services.
- Review PAM modules and unusual modification dates.
- Use constant-time comparisons and rate-limit authentication.

## References

- [0xdf — Toby](https://0xdf.gitlab.io/2022/04/16/htb-toby.html)
- [IppSec — Toby](https://www.youtube.com/watch?v=XROkuXKgeg8)
- [Hack The Box — Toby](https://app.hackthebox.com/machines/toby)
