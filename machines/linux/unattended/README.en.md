---
machine: Unattended
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, nginx-alias, lfi, session-poisoning, initrd, privesc]
---

# Unattended — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Blind SQLi in `index.php?id=` is slow to dump; an nginx alias without a slash (`dev../html/index.php`) leaks source. SQLi becomes LFI, a PHP session is poisoned and `www-data` follows. The `checkrelease` table runs commands and gives `guly`; the `grub` group allows reading the initrd, whose `uinitrd` generates root's password.

## Recon

```bash
nmap -Pn -sCV -p80,443 <IP>
```

- `80`/`443` nginx 1.10.3 with `nestedflanders.htb` and `www.nestedflanders.htb`.
- `index.php?id=` loads pages by ID.
- `gobuster` finds `/dev`, `/html` and asset paths.

## Enumeration

`id=587'` returns the main page and `id=587' and 1=1-- -` returns page 587: blind SQLi. Dumping the database is slow. A misconfigured nginx alias escapes the directory:

```bash
curl -s -k https://www.nestedflanders.htb/dev../html/index.php
```

The source reveals the query and include path.

## Foothold

SQLi controls the included file. Write a PHP webshell into a cookie, locate the session file (`/var/lib/php/sessions/sess_<ID>`) and include it to run as `www-data`.

```text
?op=/var/lib/php/sessions/sess_<PHPSESSID>
```

## Lateral movement

MySQL credentials are in the source. The config table holds `checkrelease` with a script list; inject a command and get `guly`.

```sql
UPDATE config SET value='/home/guly/checkbase.pl;bash -c "..."' WHERE name='checkrelease';
```

## Privilege escalation

`guly` is in the `grub` group and can read `/boot/initrd.img-4.9.0-8-amd64`. Decompress it with `zcat` and `cpio`; `scripts/local-top/cryptroot` calls `/sbin/uinitrd` with a fixed string. Running it prints root's password.

```bash
zcat /boot/initrd.img-4.9.0-8-amd64 | cpio -idm
./sbin/uinitrd c0m3s3f0ss34nt4n1
su root
```

## Evidence

- Blind SQLi in `id`.
- nginx alias and source.
- LFI/session poisoning and `www-data`.
- `checkrelease` and `guly`.
- initrd, `uinitrd` and root.

## Lessons learned

- A slow SQLi may have a faster server-configuration path.
- An nginx alias without a slash allows traversal.
- PHP session files are an inclusion target.
- Configuration tables can run commands.
- A readable initrd can contain root's password.

## Mitigation and detection

- Parameterize queries and use allowlists.
- Fix nginx aliases and block traversal.
- Store sessions outside the webroot and escape cookies.
- Do not run commands from the database.
- Restrict `/boot` access and protect initrd.

## References

- [0xdf — Unattended](https://0xdf.gitlab.io/2019/08/24/htb-unattended.html)
- [IppSec — Unattended](https://www.youtube.com/watch?v=2SATzCQY0Zw)
- [Hack The Box — Unattended](https://app.hackthebox.com/machines/unattended)
