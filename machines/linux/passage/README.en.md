---
machine: Passage
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, cutenews, file-upload, hash, ssh, usbcreator, dbus, privesc]
---

# Passage — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

CuteNews 2.1.2 allows uploading a PHP avatar with a webshell in the EXIF comment. Users are stored as base64 files under `cdata/users`; decoding them yields SHA-256 hashes, one for `paul`. His SSH key also authenticates `nadav`, who is in the sudo group but does not know his password; USBCreator allows arbitrary file writes as root without a password.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 7.2 and `80` Apache on Ubuntu 16.04.
- The site is a blog with an RSS link to `/CuteNews/rss.php`.
- RSS reveals CuteNews 2.1.2.

## Enumeration

Search the version on Exploit-DB: there is an authenticated arbitrary upload. Register an account, create a PNG with `exiftool -Comment='<?php system($_GET["cmd"]); ?>'` and upload it as an avatar with a `.php` extension. The webshell lands in `/CuteNews/uploads/avatar_<user>_avatar.php`.

## Foothold

The webshell runs as `www-data`. In `cdata/users` each user is a PHP file with a base64 line; decode every line to extract emails and SHA-256 hashes. Crack `paul`'s hash and use `su paul`.

```bash
# avatar webshell
exiftool -Comment='<?php system($_GET["cmd"]); ?>' avatar.png
# USBCreator
gdbus call --system --dest com.ubuntu.USBCreator \
  --object-path /com/ubuntu/USBCreator \
  --method com.ubuntu.USBCreator.Image /dev/shm/passwd /etc/passwd true
```

## Lateral movement

`/home/paul/.ssh` contains a key pair; the public key is also in `nadav`'s `authorized_keys`. The private key allows SSH as `nadav`, who is in the sudo group.

## Privilege escalation

`nadav` does not know his password, but the D-Bus service `com.ubuntu.USBCreator` exposes `Image` to copy files as root without authentication. Copy a modified `/etc/passwd` with a passwordless user or overwrite `/etc/shadow`; then `su` gives root.

## Evidence

- CuteNews 2.1.2 and PHP avatar.
- Base64 files with hashes in `cdata/users`.
- `paul` hash and SSH key shared with `nadav`.
- USBCreator and arbitrary write as root.

## Lessons learned

- Old CMSs store users in encoded flat files.
- A `.php` extension on an image upload may execute.
- SSH keys are reused across accounts.
- A privileged D-Bus service can bypass sudo policy.

## Mitigation and detection

- Update CuteNews and validate file type/content.
- Store users in a database with bcrypt/Argon2.
- Rotate SSH keys and restrict `authorized_keys`.
- Disable USBCreator or restrict its D-Bus interface.

## References

- [0xdf — Passage](https://0xdf.gitlab.io/2021/03/06/htb-passage.html)
- [IppSec — Passage](https://www.youtube.com/watch?v=kbw4_4jUP_U)
- [Hack The Box — Passage](https://app.hackthebox.com/machines/passage)
