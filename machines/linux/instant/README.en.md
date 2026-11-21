---
machine: Instant
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, android, apk, jwt, swagger, directory-traversal, solarputty, privesc]
---

# Instant — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The Android APK is decompiled and reveals the `mywalletv1.instant.htb` and `swagger-ui.instant.htb` subdomains plus an embedded administrator JWT. That token accesses the API and its documentation; an endpoint allows directory traversal and file reads, which retrieves `shirohige`'s SSH key. `/opt/backups/Solar-PuTTY/` contains a SolarPuTTY `sessions-backup.dat`; decrypting it recovers the root password and `su` completes the box.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH 9.6p1 Ubuntu.
- `80`: Apache httpd 2.4.58.

```bash
echo '<IP> instant.htb mywalletv1.instant.htb swagger-ui.instant.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://instant.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The main site distributes an Android application (`instant.apk`). It is unzipped and analyzed with `jadx-gui`; the code reveals:

- The `mywalletv1.instant.htb` API URL.
- The Swagger documentation at `swagger-ui.instant.htb`.
- An administrator JWT written into the code.
- The login flow and wallet endpoints.

```bash
unzip instant.apk -d apk
jadx-gui instant.apk
```

## Foothold

The embedded JWT is sent as `Authorization: Bearer` to the API. Swagger documents an endpoint that takes a filename; the parameter allows `../` and becomes an arbitrary read. It reads `/etc/passwd`, `user.txt` and `shirohige`'s private SSH key.

```bash
curl -s 'http://mywalletv1.instant.htb/api/v1/admin/read/log?log=../../../home/shirohige/.ssh/id_rsa' \
  -H 'Authorization: Bearer <JWT>'
```

The key is reconstructed and SSH logs in as `shirohige`.

## Lateral movement

There is no second host. The home has `logs/` and `projects/` with the API code. Enumeration focuses on configuration files and credentials saved by desktop tools.

## Privilege escalation

`/opt/backups/Solar-PuTTY/` contains `sessions-backup.dat`, a SolarPuTTY session file. SolarPuTTY encrypts credentials with a master password; the public `SolarPuttyDecrypt` (C#) and `SolarPuttyCracker` (Python) tools decrypt them. The recovered password is root's, and `su` provides the shell.

```bash
python3 SolarPuttyCracker.py sessions-backup.dat -w /usr/share/wordlists/rockyou.txt
su root
```

## Evidence

- Decompiled APK with subdomains and an embedded JWT.
- Swagger request with the administrator token.
- Directory traversal and reads of `/etc/passwd` and the SSH key.
- SSH session as `shirohige`.
- Decrypted `sessions-backup.dat` and root password.
- `id` with UID 0.

## Lessons learned

- An APK is code and can contain secrets and internal endpoints.
- JWTs embedded in clients are not secret.
- A filename parameter without normalization allows traversal.
- Session-management tools store credentials that can be decrypted.
- Password reuse between the desktop and root is a direct risk.

## Mitigations and detection

- Do not ship secrets or administrator tokens inside mobile applications.
- Validate and normalize paths; use an identifier instead of a filename.
- Enforce per-object and per-user authorization in the API.
- Encrypt sessions with strong passwords and do not reuse root's.
- Rotate credentials and review session files in home directories.
- Alert on `../` requests, long-lived JWTs and `su` to root.

## References

- [0xdf — Instant](https://0xdf.gitlab.io/2025/03/01/htb-instant.html)
- [IppSec — Instant](https://www.youtube.com/watch?v=Oyh84PHjzsQ)
- [Hack The Box — Instant](https://app.hackthebox.com/machines/instant)
- [Knowledge — SolarPuTTY credential recovery](../../../knowledge/linux/solarputty-credential-recovery.en.md)
