---
machine: RedCross
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, xss, haraka, postgresql, nss, bof, rop]
---

# RedCross — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A portal with several vhosts allows an administrator cookie to be obtained through XSS or the registration flow itself. From the panel the firewall is opened and Haraka is reached, vulnerable to RCE, or user management is used to inject into PostgreSQL and create a jail account. From `penelope`, three paths lead to root: a sudoers-gid user, `unixnssroot` credentials, or a buffer overflow in `iptctl`.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,443 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u https://<DOMAIN> -H "Host: FUZZ.<DOMAIN>" -k
```

## Enumeration

- `intra.redcross.htb` has a contact form and `admin.redcross.htb` an administration panel.
- The panel opens firewall rules and manages jail users.
- Haraka on port 25 and local PostgreSQL complete the surface.

## Initial access

XSS in the contact form steals the administrator cookie; alternatively, registration returns a valid cookie. With panel access, port 25 is opened and Haraka is exploited for a shell, or the user-management SQL injection creates a jail account and logs in as `penelope`.

## Privilege escalation

Path 1: insert a user with gid 27 (sudo) and run `sudo su`. Path 2: read `/etc/nss-pgsql-root.conf`, connect as `unixnssroot` and insert a user with uid 0. Path 3: the SUID `iptctl` copies the action with `strcpy` and overflows the stack; ROP calls `execvp` to launch a shell.

## Evidence

- Administrator cookie and panel access.
- PostgreSQL-created account and shell as `penelope`.
- Privileged uid/gid user or ROP in `iptctl`.

## Lessons learned

- An NSS-backed jail inherits flaws from the database that feeds it.
- Session cookies and contact forms are a path into the panel.
- SUID binaries with fixed buffers remain relevant.

## Mitigation and detection

- Move the jail to a least-privilege, audited mechanism.
- Sanitize XSS and use HttpOnly/SameSite cookies.
- Build with stack protector, ASLR and no unnecessary SUID.

## References

- [0xdf — RedCross](https://0xdf.gitlab.io/2019/04/13/htb-redcross.html)
- [IppSec — RedCross](https://www.youtube.com/watch?v=-GNyDEQ9UDU)
- [Hack The Box — RedCross](https://app.hackthebox.com/machines/redcross)
