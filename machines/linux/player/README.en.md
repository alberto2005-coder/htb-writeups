---
machine: Player
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, ffmpeg, lshell, privesc]
---

# Player — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Vhosts reveal a site using HS256 JWTs; a backup exposes the signing key and allows forging an administrator `access_code`. The panel uses ffmpeg on AVI files and the demuxer reflects local file contents. Recover `telegen` credentials, escape lshell with `su -s /bin/bash` and reach Codiad, where a root cron includes a writable file or deserializes `merge.log`.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with several vhosts.
- `ffuf -H 'Host: FUZZ.player.htb'` finds `staging`, `chat`, `admin` and `api`.
- The main vhost uses an API with JWTs.

## Enumeration

- `/backup/` contains a file with the HS256 JWT `secret`.
- The token includes `access_code`; forging it with the `admin` role opens the panel.
- The panel uploads media and calls `ffmpeg` to generate thumbnails.

## Foothold

Sign a JWT with the key and an administrator `access_code`. In the panel, a crafted AVI makes ffmpeg's demuxer read a local file and reflect it in the error or thumbnail; this reads `/etc/passwd` and the application configuration.

```bash
python3 jwt_tool.py <TOKEN> -S hs256 -p '<SECRET>' -I -pc access_code -pv admin
```

## Lateral movement

File read reveals `telegen` credentials. The account uses lshell, which restricts commands; `su -s /bin/bash telegen` opens a normal bash without a password. The home directory provides access to Codiad.

```bash
su -s /bin/bash telegen
```

## Privilege escalation

Codiad has a webshell at `components/filemanager/controller.php`. A root cron runs `buff.php`, which includes a writable file or deserializes `merge.log`; place the payload and wait for execution.

```bash
echo '<?php system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash"); ?>' > /var/www/html/codiad/merge.log
```

## Evidence

- JWT key in `/backup/` and forged admin token.
- AVI causing ffmpeg local file read.
- `telegen` credentials and lshell escape.
- `merge.log` processed by the root cron.

## Lessons learned

- A leaked JWT key invalidates all authentication.
- ffmpeg processes untrusted input and can leak files.
- A restricted shell is not an unprivileged account.

## Mitigation and detection

- Rotate the JWT key and keep backups outside the webroot.
- Run ffmpeg in a sandbox without filesystem access.
- Review crons that include or deserialize webroot files.

## References

- [0xdf — Player](https://0xdf.gitlab.io/2020/01/18/htb-player.html)
- [IppSec — Player](https://www.youtube.com/watch?v=JpzREo7XLOY)
- [Hack The Box — Player](https://app.hackthebox.com/machines/player)
