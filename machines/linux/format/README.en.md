---
machine: Format
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, php, gitea, lfi, redis, nginx, ssti]
---

# Format — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A PHP microblog and its Gitea repository expose the source and an arbitrary file read/write primitive. A bad Nginx `proxy_pass` rule leaves Redis reachable through a Unix socket; poisoning the database grants the `pro` role, a webshell is written into the enabled upload directory, and `www-data` is obtained. Shared Redis credentials lead to `cooper`, and a root-run Python script with unsafe interpolation completes the chain.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,3000 <IP>
```

- SSH, Nginx/PHP and Gitea on port 3000.
- `microblog.htb` and `app.microblog.htb`; user blogs use subdomains.
- `feroxbuster` and `ffuf` reveal `app`, `gitea` and edit endpoints.

## Enumeration

- The Gitea repository exposes the PHP application and Nginx configuration.
- Blog editing accepts a path that is used to read and write files.
- Nginx forwards a prefix to `unix:/var/run/redis/redis.sock`.
- Redis stores account state and the role that controls upload access.

## Foothold

Use arbitrary read to recover the source and arbitrary write to change the Redis state. Assigning the `pro` role creates an executable upload directory. Write a minimal PHP file and request it to run commands as `www-data`.

```bash
curl -s "http://app.microblog.htb/edit.php?..."
redis-cli -s /var/run/redis/redis.sock
```

The key is chaining a file primitive with an internal service that trusts stored content; no public CVE is required.

## Privilege escalation

Redis contains a password reused by `cooper`. After SSH access, enumerate a Python script run by root that interpolates user-controlled text. Inject a template expression to read a privileged file and complete the escalation.

```bash
sudo -l
find / -writable -type f 2>/dev/null | head
```

## Evidence

- Gitea repository with the vulnerable code.
- Edit request reading and writing outside the blog directory.
- Redis response with the modified role.
- `id` output from the webshell and SSH access as `cooper`.

## Lessons learned

- An LFI with write access is often enough to turn an internal service into RCE.
- Unix sockets are not a security boundary when the proxy allows arbitrary paths.
- Reviewing source code beats blind payload testing.

## Mitigations and detection

- Canonicalize and confine read/write paths to a base directory.
- Do not expose Redis through `proxy_pass`; require socket authentication.
- Alert on writes to web directories and PHP access to `redis.sock`.
- References: HTB Format, 0xdf and CWE-22/CWE-94.

## References

- <https://www.hackthebox.com/machines/Format>
- <https://0xdf.gitlab.io/2023/09/30/htb-format.html>
- <https://cwe.mitre.org/data/definitions/22.html>
- <https://attack.mitre.org/techniques/T1190/>
