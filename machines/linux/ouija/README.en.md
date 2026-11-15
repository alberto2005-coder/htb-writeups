---
machine: Ouija
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, haproxy, request-smuggling, hash-extension, php-extension, integer-overflow]
---

# Ouija — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Request smuggling in HAProxy reaches an internal development site. API details enable a hash length extension attack to forge an administrator key and read an SSH key. Root exploits an integer overflow in a custom PHP module to obtain arbitrary write.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,8080 <IP>
# CL.TE request smuggling
curl --path-as-is -H "Content-Length: 6" -H "Transfer-Encoding: chunked" http://ouija.htb/
# Hash length extension
hashpump -s <SIG> -d "user=guest" -a "&admin=1" -k <LEN>
# API
curl -H "X-API-Key: <FORGED>" http://ouija.htb/api/admin
# PHP module
php -i | grep extension_dir
gdb -q -p <PID>
python3 exploit.py
```

## Enumeration

- HAProxy in front of frontend and backend with inconsistent parsing.
- Development site and API signed as `hash(secret || data)`.
- Native PHP module with an unchecked integer.

## Initial access

Send a request with conflicting `Content-Length` and `Transfer-Encoding` so HAProxy and the backend disagree and the backend processes an internal route. The development site leaks the API and its signature format; use `hashpump` to extend the message and forge the administrator key.

## Privilege escalation

The admin API reads an SSH key and grants host access. Find a compiled PHP module that computes an index from an integer; send a value that overflows and overwrites stack variables, which is used for arbitrary write and root execution.

## Evidence

- Smuggled request accepted by the backend.
- Forged administrator key and SSH key read.
- Module overflow and root shell.

## Lessons learned

- Proxy and backend must normalize requests identically.
- `hash(secret || data)` is vulnerable to length extension.
- Native modules need integer validation and bounds checks.

## Mitigation and detection

- Reject ambiguous headers and normalize at both ends.
- Use HMAC instead of secret concatenation.
- Build with `-fstack-protector` and review native modules.

## References

- [0xdf — Ouija](https://0xdf.gitlab.io/2024/05/18/htb-ouija.html)
- [HAProxy — Configuration](https://docs.haproxy.org/)
- [Hack The Box — Ouija](https://app.hackthebox.com/machines/ouija)
