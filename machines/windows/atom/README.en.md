---
machine: Atom
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, smb, electron, updater, redis]
---

# Atom — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An SMB update share is writable and the Electron application trusts the `electron-updater` manifest. Publish a malicious update and obtain execution; Redis stores the PortableKanban configuration with the administrator password.

## Reconnaissance

```bash
nmap -Pn -sCV -p80,445,6379 <IP>
smbclient -N -L //<IP>
smbclient -N //<IP>/Software_Updates
# Replace latest.yml and the package with a payload
redis-cli -h <IP> -p 6379
keys *
get <KEY>
```

## Enumeration

- SMB exposes `Software_Updates` with write access.
- The Electron app reads a `latest.yml` and downloads the package.
- Redis on `6379` contains PortableKanban keys.

## Initial access

Replace the update manifest and package with a controlled executable. The application downloads and runs it without validating the publisher signature, yielding a session as the user who opened Atom.

## Privilege escalation

Redis contains the PortableKanban file with the encrypted administrator password. Recover the key, decrypt it and use it over WinRM or SMB as Administrator.

## Evidence

- Modified `latest.yml` on the SMB share.
- Updater child process running the payload.
- Decrypted PortableKanban key and administrative access.

## Lessons learned

- A writable update channel is code execution.
- Package signatures must be validated on the client and server.
- Unauthenticated Redis exposes desktop application secrets.

## Mitigation and detection

- Restrict write access to the update share and sign packages.
- Require TLS and validate the manifest before downloading.
- Protect Redis and avoid recoverable password storage.

## References

- [0xdf — Atom](https://0xdf.gitlab.io/2021/07/10/htb-atom.html)
- [Electron — autoUpdater](https://www.electronjs.org/docs/latest/api/auto-updater)
- [Hack The Box — Atom](https://app.hackthebox.com/machines/atom)
