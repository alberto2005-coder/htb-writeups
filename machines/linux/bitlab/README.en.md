---
machine: Bitlab
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, gitlab, webshell, postgresql, reversing]
---

# Bitlab — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

GitLab Community Edition leaks credentials on the login page. With `clave`'s session, a webshell is published in a project and `www-data` is obtained; a PostgreSQL tunnel reveals `clave`'s password. In the home directory, `RemoteConnection.exe` contains the root password used for `putty`, enabling the final login.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -u http://<IP>/FUZZ
```

## Enumeration

- The site runs GitLab CE and lists projects owned by `root`.
- The login HTML leaks `clave` credentials.
- The host listens on PostgreSQL 5432; GitLab and PostgreSQL run in containers.

## Initial access

Log in to GitLab with the leaked credentials and create or modify a project containing a webshell. When the change is committed, the server renders it and executes commands as `www-data`.

## Privilege escalation

Open an SSH tunnel to PostgreSQL, query the users and recover `clave`'s password. The home directory holds `RemoteConnection.exe`, which launches `putty` with `-pw`; `strings`, IDA and `x32dbg` reveal the root password, valid over SSH.

## Evidence

- Credentials visible in the GitLab HTML.
- Webshell commit and execution as `www-data`.
- `putty -pw` string in memory and SSH access as root.

## Lessons learned

- Source code and HTML can leak secrets.
- SSH tunnels turn internal services into reachable ones.
- Desktop binaries may contain plaintext credentials.

## Mitigation and detection

- Rotate exposed credentials and review generated HTML.
- Isolate GitLab and PostgreSQL; do not reuse passwords.
- Never store secrets in binaries or process arguments.

## References

- [0xdf — Bitlab](https://0xdf.gitlab.io/2020/01/11/htb-bitlab.html)
- [IppSec — Bitlab](https://www.youtube.com/watch?v=Fxq6oZ-H-xI)
- [Hack The Box — Bitlab](https://app.hackthebox.com/machines/bitlab)
