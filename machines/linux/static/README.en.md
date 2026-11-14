---
machine: Static
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, totp, vpn, xdebug, php-fpm, format-string, easy-rsa]
---

# Static — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A corrupted gzip SQL backup allows recovery of the TOTP seed and access to the internal panel, which provides a VPN configuration. On the internal network, a web host with xdebug allows RCE and pivoting to the PKI host, where PHP-FPM is vulnerable to CVE-2019-11043. The final escalation abuses `ersatool`, which has `cap_setuid` and a format string that overwrites `ERSA_DIR` to run a controlled `easyrsa` as root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,2222,8080 <IP>
gobuster dir -u http://<IP>:8080 -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt
```

## Enumeration

- Two SSH versions suggest Docker containers.
- The SQL backup is truncated but still holds the TOTP seed.
- The internal panel lists `172.20.0.10` (web) and `172.20.0.11` (pki).

## Initial access

Repair the gzip and extract the TOTP seed to generate a code and enter the panel, which provides a VPN configuration. With the VPN, reach `172.20.0.10`, whose xdebug exposes remote execution and yields `www-data`. Pivot to `172.20.0.11`, where CVE-2019-11043 in PHP-FPM provides a shell as `www-data`.

## Privilege escalation

`ersatool` has `cap_setuid` and a format string in `printCN`. Leak the `EXT` address, calculate `ERSA_DIR`, overwrite it with a writable path and place an `easyrsa` script that copies bash and makes it SUID. Running `create` makes the binary call `system` after `setuid(0)`, yielding root.

## Evidence

- Valid TOTP and downloaded VPN configuration.
- Shells on `web` and `pki` through xdebug and PHP-FPM.
- Overwritten `ERSA_DIR` and executed SUID bash.

## Lessons learned

- Corrupted backups may retain enough secrets.
- xdebug must never be exposed in production.
- A `cap_setuid` capability turns a binary into potential root.

## Mitigation and detection

- Encrypt backups and protect TOTP seeds.
- Disable xdebug and update PHP-FPM/Nginx.
- Drop unnecessary capabilities and review C format strings.

## References

- [0xdf — Static](https://0xdf.gitlab.io/2021/12/18/htb-static.html)
- [IppSec — Static](https://www.youtube.com/watch?v=XZd-pQTu4vU)
- [Hack The Box — Static](https://app.hackthebox.com/machines/static)
