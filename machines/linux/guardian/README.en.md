---
machine: Guardian
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, php, gitea, phpspreadsheet, csrf, lfi, privesc]
---

# Guardian — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The university portal has an IDOR in the chat that leaks a lecturer's Gitea password. The repository reveals a vulnerable PhpSpreadsheet: a malicious XLSX runs XSS and steals the lecturer session. A CSRF with a weak token creates an administrator; as admin, an LFI with `php://filter` gives RCE and `www-data`. The database hash cracks and the password is reused on `jamil`, who can run `utilities.py` as `mark`. `safeapache2ctl` reads root files and loads a module to obtain a SUID shell.

## Recon

```bash
nmap -Pn -sCV -p22,80,443,3000 <IP>
```

- `80/443` serve `guardian.htb` and `portal.guardian.htb`.
- `ffuf` finds `gitea.guardian.htb` and `admin.guardian.htb`.
- The portal allows student registration and a chat.

## Enumeration

- The chat uses `chat_users[0]` and `chat_users[1]`; changing the IDs shows other conversations (IDOR).
- An administrator message hands over `jamil.enockson`'s Gitea password.
- The `portal.guardian.htb` repository contains the source and the PhpSpreadsheet version.

## Foothold

Grade uploads use PhpSpreadsheet and accept XLSX. A sheet with a malicious formula runs XSS when the lecturer opens the file; the stolen cookie grants access to their account. A CSRF with a predictable token creates an admin user.

```text
http://portal.guardian.htb/student/chat.php?chat_users[0]=1&chat_users[1]=2
```

## Lateral movement

As admin, `admin/reports.php` includes the `report` parameter and allows `php://filter`. A conversion chain writes a webshell and yields `www-data`. The database hash cracks and the password works over SSH for `jamil`.

```bash
ssh jamil@guardian.htb
```

`jamil` can run `/opt/scripts/utilities/utilities.py` as `mark`; `utils/status.py` is group-writable and is modified to run a shell as `mark`.

## Privilege escalation

`mark` runs `safeapache2ctl` with a configuration he owns. The `-f` option allows `Include /root/root.txt` to read the flag, and `LoadModule` loads a `.so` that creates a SUID copy of bash before failing.

```bash
printf 'LoadModule evil /home/mark/confs/evil.so\n' > /home/mark/confs/0xdf.conf
safeapache2ctl -f /home/mark/confs/0xdf.conf
/tmp/0xdf -p
```

## Evidence

- Chat IDOR and Gitea password.
- XLSX with XSS and lecturer session.
- CSRF and admin creation.
- LFI with filter chain and `www-data`.
- Cracked hash, `utilities.py` and `safeapache2ctl`.

## Lessons learned

- An IDOR in a chat leaks conversations and credentials.
- Processing user files with PhpSpreadsheet exposes XSS and worse.
- An Apache wrapper accepting `-f` and user modules is root.

## Mitigation and detection

- Validate the session user on every chat and never trust IDs.
- Update PhpSpreadsheet and isolate document uploads.
- Use strong CSRF tokens and disallow `Include`/`LoadModule` in user configurations.
- Run `utilities.py` with least privilege and review writable scripts.

## References

- [0xdf — Guardian](https://0xdf.gitlab.io/2026/02/28/htb-guardian.html)
- [IppSec — Guardian](https://www.youtube.com/watch?v=Fzt-oZX0Mzo)
- [Hack The Box — Guardian](https://app.hackthebox.com/machines/guardian)
