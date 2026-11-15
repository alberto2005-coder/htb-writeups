---
machine: MonitorsThree
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, cacti, sqli, duplicati, privesc]
---

# MonitorsThree — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The main site's password reset is injectable and leaks the administrator hash, which cracks. Those credentials open Cacti 1.2.26, vulnerable to CVE-2024-25642: package import allows a PHP upload and `www-data`. The Cacti database yields `marcus`'s password, and he can reach Duplicati; a backup of the root filesystem reads the flag or writes an SSH key.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` the MonitorsThree site.
- `ffuf` with `Host: FUZZ.monitorsthree.htb` finds `cacti.monitorsthree.htb`.
- Port 8084 is filtered and does not respond initially.

## Enumeration

- `/forgot_password.php` concatenates the username into the query.
- A `UNION` returns the administrator's MD5 hash and email.
- The hash cracks and the same credentials work in Cacti.

```bash
sqlmap -u 'http://monitorsthree.htb/forgot_password.php' --data 'username=admin' --batch --dump
```

## Foothold

Cacti 1.2.26 is vulnerable to CVE-2024-25642. Build a malicious package, import it from `Import/Export` and the PHP lands in `resource/`, where it runs.

```bash
php cve-2024-25642.php
curl 'http://cacti.monitorsthree.htb/cacti/resource/<FILE>.php'
```

## Lateral movement

Cacti configuration holds database credentials; `user_auth` contains `marcus`'s hash. Crack it and use it over SSH. `marcus` can tunnel to the Duplicati port.

```bash
ssh -L 8200:127.0.0.1:8200 marcus@<IP>
```

## Privilege escalation

Duplicati runs as root and can back up `/`. Restore it to a controlled path to read `/root/root.txt`, or add a public key to `/root/.ssh/authorized_keys` and log in over SSH.

```text
Source: /root
Target: /tmp/restore
```

## Evidence

- SQLi in the reset and administrator hash.
- Cacti 1.2.26 and CVE-2024-25642.
- `marcus` password and Duplicati tunnel.
- Root backup and SSH key.

## Lessons learned

- A password reset can be SQLi with output.
- Cacti package import runs content when unvalidated.
- A root backup tool with a local interface is direct escalation.

## Mitigation and detection

- Parameterize the reset and use single-use tokens.
- Update Cacti and restrict package import.
- Run Duplicati unprivileged and isolate its interface.

## References

- [0xdf — MonitorsThree](https://0xdf.gitlab.io/2025/01/18/htb-monitorsthree.html)
- [IppSec — MonitorsThree](https://www.youtube.com/watch?v=4y2gp_GTBqQ)
- [Hack The Box — MonitorsThree](https://app.hackthebox.com/machines/monitorsthree)
