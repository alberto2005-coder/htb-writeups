---
machine: Silentium
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, flowise, password-reset, docker, gogs, symlink]
---

# Silentium — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The staging subdomain runs Flowise. The password-reset endpoint returns the token in its response and allows `ben`'s account to be taken over; version 3.0.5 is vulnerable to CVE-2025-59528 and executes code as root in the container. Environment variables leak a password reused by `ben` over SSH. On the host, Gogs 0.13.3 allows CVE-2025-8110 and, through a symlink, writes a key into `/root/.ssh`.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<DOMAIN> -H "Host: FUZZ.<DOMAIN>"
```

## Enumeration

- `staging.silentium.htb` shows a Flowise login and the API reveals version 3.0.5.
- Password reset returns the token in the response body.
- On the host, Gogs 0.13.3 listens on `127.0.0.1:3001` and runs as root.

## Initial access

Enumerate a valid email through reset and use the returned token to change `ben`'s password. Once authenticated, abuse a node that passes configuration to JavaScript's `Function` constructor (CVE-2025-59528) and execute code as root inside the container. Environment variables contain `ben`'s password, reused over SSH.

## Privilege escalation

As `ben`, reach Gogs on localhost. CVE-2025-8110 allows a repository with a symlink to `/root/.ssh` and the `PutContents` API to write `authorized_keys` outside the repository. The write happens before the commit fails, so SSH access as root is obtained.

## Evidence

- Reset response containing the token and a `ben` session.
- Container execution and Docker hostname.
- Gogs symlink and SSH access as root.

## Lessons learned

- Never return recovery tokens in the response.
- Dynamic constructors turn configuration into code execution.
- Path validation must resolve symlinks before writing.

## Mitigation and detection

- Send tokens only over a secure, single-use channel.
- Isolate nodes and disable `Function` with user input.
- Resolve paths with `realpath` and confine writes to the repository.

## References

- [0xdf — Silentium](https://0xdf.gitlab.io/2026/09/12/htb-silentium.html)
- [IppSec — Silentium](https://www.youtube.com/watch?v=B9lVpmiCORQ)
- [Hack The Box — Silentium](https://app.hackthebox.com/machines/silentium)
