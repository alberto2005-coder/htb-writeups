---
machine: Intense
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, hash-length-extension, snmp, buffer-overflow, rop, privesc]
---

# Intense — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SQLi in the login leaks the admin hash; a hash length extension attack forges the cookie and grants access. A log API with traversal reads SNMP write credentials, and `snmp-shell` gives a shell. On localhost, `note_server` has a logic bug and a canary-protected buffer overflow; ROP with a libc leak ends in root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
nmap -Pn -sU -p161 <IP>
```

- `22` SSH, `80` nginx with a notes app and `161/udp` SNMP.
- The app supports registration, login and log export.
- Source code is available on the website.

## Enumeration

- Login is SQLi-vulnerable; the admin hash leaks but does not crack.
- The code shows the session uses `sha1(secret + username)` and compares the hash.
- `hash_extender` appends an admin user and signs the cookie.

```bash
hash_extender --data admin --secret <LEN> --append '&user=admin' --signature <HASH> --format sha1
```

## Foothold

The log API takes a path and allows traversal. Read `/etc/snmp/snmpd.conf` and SNMP write credentials. `snmp-shell` gives a reverse shell.

```bash
snmp-shell -v 2c -c <COMMUNITY> <IP>
```

## Lateral movement

The shell is `snmp`. On localhost, `note_server` listens on 5001 and its code is in the home. The binary has a logic bug: it can write past the buffer and read the canary and return address.

## Privilege escalation

Leak the canary and a libc address with the read primitive; build a ROP chain with `dup2`, `execv` and `/bin/sh`, and connect to port 5001 through an SSH tunnel. The process runs as root.

```bash
python3 pwn_note_server.py remote
```

## Evidence

- SQLi and admin hash.
- Hash extension and forged cookie.
- Log traversal and SNMP credentials.
- `snmp-shell` and `snmp` user.
- Buffer overflow, ROP and root.

## Lessons learned

- `sha1(secret + data)` is vulnerable to hash extension.
- Logs and configuration expose SNMP credentials.
- SNMP write access runs commands.
- A logic bug can turn an overflow into a leak and ROP.

## Mitigation and detection

- Use HMAC and constant-time comparisons for sessions.
- Restrict the log API and normalize paths.
- Use SNMPv3 and read-only access.
- Build with canaries, ASLR and PIE; review internal binaries.

## References

- [0xdf — Intense](https://0xdf.gitlab.io/2020/11/14/htb-intense.html)
- [IppSec — Intense](https://www.youtube.com/watch?v=nBg6zUalb7c)
- [Hack The Box — Intense](https://app.hackthebox.com/machines/intense)
