---
machine: CCTV
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, zoneminder, sqli, tcpdump, motioneye]
---

# CCTV — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

ZoneMinder 1.37.63 keeps default credentials and is vulnerable to CVE-2024-51482, a blind SQLi in event handling. Dump the database, crack `mark`'s bcrypt hash and log in over SSH. `mark` can capture traffic and sees `sa_mark`'s password in clear text; it opens motionEye on localhost, where CVE-2025-60787 runs commands as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 24.04 and `80/tcp` Apache serving `cctv.htb`.
- `/zm/` serves ZoneMinder 1.37.63 and accepts `admin:admin`.
- No additional subdomains; the rest of the site is static.

## Enumeration

- Version 1.37.63 is affected by CVE-2024-51482, a blind SQLi in `AddMonitorsTable`.
- `sqlmap` confirms time-based injection and enumerates users and bcrypt hashes.
- `mark`'s hash cracks with `hashcat -m 3200`.

## Foothold

Use `sqlmap` with the session cookie to dump the database, then log in over SSH as `mark`.

```bash
sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=...' --cookie='ZMSESSID=<SESSION>' --batch --dump
hashcat -m 3200 zm.hashes rockyou.txt
ssh mark@cctv.htb
```

## Lateral movement

`mark` is in the `tcpdump` group, so capture port `5000` traffic. The camera management protocol sends `sa_mark`'s password in clear text; reuse it with `su`.

## Privilege escalation

motionEye listens on `localhost:8765`. Create an SSH tunnel, log in as `admin` with `sa_mark`'s password, and exploit CVE-2025-60787 in the image filename to run commands as root.

```bash
ssh -L 8765:localhost:8765 mark@cctv.htb
# In motionEye: Settings -> Still Images -> filename
# CVE-2025-60787 payload
```

## Evidence

- ZoneMinder with default credentials and confirmed SQLi.
- Cracked `mark` hash and `tcpdump` capture.
- motionEye access and root execution.

## Lessons learned

- Default credentials still appear in video surveillance products.
- Blind SQLi is enough to dump hashes when the session is valid.
- Unencrypted management traffic exposes reusable passwords.

## Mitigation and detection

- Update ZoneMinder and motionEye; change default credentials.
- Encrypt the management protocol and segment cameras.
- Restrict `tcpdump` and review unauthorized captures.

## References

- [0xdf — CCTV](https://0xdf.gitlab.io/2026/07/11/htb-cctv.html)
- [IppSec — CCTV](https://www.youtube.com/watch?v=C60J33Mbd5E)
- [Hack The Box — CCTV](https://app.hackthebox.com/machines/cctv)
