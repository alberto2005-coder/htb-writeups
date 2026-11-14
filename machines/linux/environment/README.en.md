---
machine: Environment
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, laravel, cve-2024-52301, filemanager, gpg, bash-env]
---

# Environment — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Laravel app in debug mode allows changing the environment through CVE-2024-52301 and entering the internal `preprod` panel. The vulnerable filemanager accepts a webshell and yields `www-data`; a GPG backup and `hish`'s private key allow `su`, while `sudo systeminfo` keeps `BASH_ENV`, which is used to run a root shell.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -u http://<DOMAIN>/FUZZ
```

## Enumeration

- The front page is a Laravel app with `APP_DEBUG=true`.
- The application has a login panel and a profile-image filemanager.
- The server uses SQLite and exposes `/home/hish` with loose permissions.

## Initial access

CVE-2024-52301 lets an attacker set the environment through a crafted query string; `preprod` bypasses the panel login. In the profile page, the filemanager fails to validate the extension and accepts a PHP file executed as `www-data`.

## Privilege escalation

Read the SQLite database and the `keyvault.gpg` backup; `hish`'s GPG keys are accessible, so copy them to a temporary home and decrypt the backup to obtain the password. `sudo -l` shows `systeminfo` with `env_keep=BASH_ENV`; point it at a script that starts bash and run it as root.

## Evidence

- Response showing the `preprod` environment and dashboard access.
- Filemanager webshell and `id` as `www-data`.
- Decrypted backup and root shell through `BASH_ENV`.

## Lessons learned

- Debug mode and environment variables can alter authentication flow.
- Backups and private keys need strict permissions.
- `env_keep` can turn an apparently harmless sudo rule into root.

## Mitigation and detection

- Disable debug and pin the environment in server configuration.
- Validate extensions and serve uploads outside the document root.
- Do not preserve `BASH_ENV` or `ENV` in sudo rules.

## References

- [0xdf — Environment](https://0xdf.gitlab.io/2025/09/06/htb-environment.html)
- [IppSec — Environment](https://www.youtube.com/watch?v=XUEr-CM3Y6Q)
- [Hack The Box — Environment](https://app.hackthebox.com/machines/environment)
