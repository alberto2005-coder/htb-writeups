---
machine: WingData
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, wingftp, cve-2025-47812, null-byte, lua, tarfile, privesc]
---

# WingData — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Wing FTP Server 7.4.3 allows anonymous access and is vulnerable to CVE-2025-47812: a null byte in the username injects Lua into the session file and gives RCE as `wingftp`. Account files hold salted hashes; one cracks and the password is reused for `wacky`. `wacky` runs a Python backup restore script as root, and CVE-2025-4517 writes outside the extraction directory with a symlink tar.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with `wingdata.htb`.
- The panel is Wing FTP Server 7.4.3 and allows anonymous access.
- `feroxbuster` enumerates `/admin`, `/login` and download paths.

## Enumeration

The server has anonymous access and a web interface. Version 7.4.3 predates 7.4.4 and is vulnerable to CVE-2025-47812: a null byte in the username injects Lua into the session file that Wing FTP executes.

## Foothold

Send a username with `%00` and a Lua statement that runs a reverse shell; the server interprets it when loading the session and gives a `wingftp` shell.

## Lateral movement

Wing FTP account files hold salted hashes. Copy and crack them with Hashcat; `wacky`'s password is reused on the system.

```bash
hashcat -m 17200 hashes.txt rockyou.txt
ssh wacky@wingdata.htb
```

## Privilege escalation

`wacky` can run the restore script as root:

```bash
sudo /usr/local/bin/python3 /opt/backup_clients/restore_backup_clients.py <BACKUP>
```

The script uses `tarfile` with the `data` filter, vulnerable to CVE-2025-4517. Build a tar with a symlink to `/root/.ssh/authorized_keys` and a path escaping the extraction directory; validation is bypassed and root's public key is written.

## Evidence

- Wing FTP 7.4.3 and anonymous access.
- CVE-2025-47812 and `wingftp` shell.
- Account hashes and `wacky`.
- Restore script as root.
- CVE-2025-4517 and root key.

## Lessons learned

- A null byte can truncate validation and smuggle code into a session file.
- Application hashes are reused on the system.
- Old `tarfile` filters do not prevent writes outside the destination.
- A root restore script is an arbitrary-write target.

## Mitigation and detection

- Update Wing FTP to 7.4.4 or later.
- Disable anonymous access and validate users.
- Use unique passwords and strong hashing.
- Update Python and validate members/symlinks on extraction.

## References

- [0xdf — WingData](https://0xdf.gitlab.io/2026/06/27/htb-wingdata.html)
- [IppSec — WingData](https://www.youtube.com/watch?v=T5VUR55e1Xg)
- [Hack The Box — WingData](https://app.hackthebox.com/machines/wingdata)
