---
machine: Joker
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, squid, tftp, werkzeug, udp, sudoedit, tar, wildcard, privesc]
---

# Joker — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

TFTP allows downloading Squid's configuration and proxy password file. Those credentials reach a localhost Werkzeug server with a Python console; the firewall blocks outbound TCP but allows UDP, so use a UDP reverse shell. A sudoedit rule with a wildcard leads to `alekos`, and a cron running `tar` with `*` allows option injection and root.

## Recon

```bash
nmap -Pn -sCV -p22,3128 <IP>
nmap -sU -p69 <IP>
```

- `22` SSH and `3128` Squid 3.5.12.
- TFTP on UDP `69`.
- Squid returns `407 Proxy Authentication Required` and reveals the `kalamari` realm.

## Enumeration

TFTP does not list directories, but `/etc/squid/squid.conf` and `/etc/squid/passwords` can be downloaded. Crack the `$apr1$` hash with hashcat mode 1600. With the authenticated proxy, scan `127.0.0.1` and find Werkzeug on port 8080.

## Foothold

The Werkzeug console runs Python. A TCP reverse shell has no outbound connectivity; enumerate the firewall and use a UDP reverse shell with `socat file:\`tty\`,raw,echo=0 udp-listen:<PORT>`. The session is `werkzeug`.

```bash
# TFTP
tftp <IP>
tftp> get /etc/squid/squid.conf
tftp> get /etc/squid/passwords
# proxy to localhost
curl -x http://<USER>:<PASS>@<IP>:3128 http://127.0.0.1:8080/
# tar wildcard
touch -- '--checkpoint=1' '--checkpoint-action=exec=/dev/shm/root.sh'```

## Lateral movement

`werkzeug` can run `sudoedit /var/www/*/*/layout.html`. Create a directory and a `layout.html` symlink to `/home/alekos/.ssh/authorized_keys`; `sudoedit` follows it and lets you insert a public key. Wildcard abuse also edits the file directly.

## Privilege escalation

A root cron runs `cd /home/alekos/development` and `tar cf /home/alekos/backup/$FILENAME *`. Create files named `--checkpoint=1` and `--checkpoint-action=exec=<script>`; the wildcard expands them as `tar` options and the script runs as root.

## Evidence

- Squid configuration and hash over TFTP.
- Authenticated proxy and Werkzeug console.
- UDP reverse shell.
- `sudoedit` with symlink/wildcard.
- `tar` wildcard as root.

## Lessons learned

- TFTP can read files when the path is known.
- An authenticated proxy can expose localhost services.
- `sudoedit` rules with wildcards are dangerous.
- Wildcards in `tar` allow option injection.

## Mitigation and detection

- Restrict TFTP and keep hashes out of readable paths.
- Limit the proxy to required destinations.
- Avoid wildcards in sudoedit; use absolute paths and `--`.
- Use `find -print0`/`xargs -0` in backups.

## References

- [0xdf — Joker](https://0xdf.gitlab.io/2020/08/13/htb-joker.html)
- [IppSec — Joker](https://www.youtube.com/watch?v=5wyvpJa9LdU)
- [Hack The Box — Joker](https://app.hackthebox.com/machines/joker)
