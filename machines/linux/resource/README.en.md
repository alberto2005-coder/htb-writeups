---
machine: Resource
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, phar, deserialization, ssh-certificates, har, bash, glob, privesc]
---

# Resource — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The ticket center allows a ZIP attachment and accesses a file through a PHAR filter, executing a webshell inside the ZIP. The database and a `.har` leak `msainristil` credentials; the ITRC container holds the old SSH CA still trusted, used to sign a key for root. On the main host, the signing API and a script run with sudo grant principals and, through an unquoted Bash comparison, leak IT's private CA key and sign a `root_user` certificate.

## Recon

```bash
nmap -Pn -sCV -p22,80,2222 <IP>
```

- `22` and `2222` SSH on different hosts, `80` nginx in front of Apache.
- Ticket app at `itrc.ssg.htb`.
- The panel creates tickets and accepts attachments; files land in `/uploads/<hash>.zip`.

## Enumeration

Create a ticket with a ZIP containing `shell.php`. The app checks existence with a controlled path; using `phar://uploads/<hash>.zip/shell` interprets the inner file as PHP and gives `www-data`. The MariaDB database contains `tickets`, `messages` and `users`; an attached `.har` includes `msainristil` credentials.

## Foothold

`msainristil` credentials work in the container over SSH (22) and 2222. `/etc/ssh` holds `ca-it` and an old ITRC CA; the old CA private key signs a key with the `root_user` principal and logs in as root in the container.

```bash
# PHAR in ticket
curl 'http://itrc.ssg.htb/ticket.php?id=<ID>&page=phar://uploads/<HASH>.zip/shell'
# comparison oracle; /dev/shm/file holds the CA candidate
sudo /opt/sign_key.sh /dev/shm/file /etc/passwd <USER> <USER> 1
# root certificate
ssh-keygen -s ca_it -z 223 -I <USER> -V -5m:forever -n root_user key.pub
```

## Lateral movement

As root in the container, read `/home/zzinter/sign_key_api.sh`, which uses a token to call `signserv.ssg.htb/v1/sign`. Request certificates with the `support` and `zzinter_temp` principals and log in to the main host as `zzinter`.

## Privilege escalation

`zzinter` can run `/opt/sign_key.sh` with sudo. The script compares `[[ $itca == $ca ]]` unquoted; a file with a wildcard makes Bash expand the pattern and the comparison succeeds only if the prefix matches. Brute-force `ca_it`'s private key character by character, sign a key with the `root_user` principal and log in as root on the main host.

## Evidence

- ZIP webshell and PHAR filter.
- `.har` with `msainristil` credentials.
- Old trusted CA and root in ITRC.
- Signing API, principals and Bash glob comparison.

## Lessons learned

- File filters and PHAR can execute code in seemingly inert files.
- `.har` files capture credentials and session tokens.
- Old SSH CAs remain trusted unless removed.
- An unquoted Bash comparison allows globbing and secret leaks.

## Mitigation and detection

- Do not accept PHP inside archives or use wrappers on uploads.
- Sanitize `.har` files and never attach sessions with credentials.
- Retire old CAs and rotate their keys.
- Quote variables in Bash comparisons and use `[[ ]]` correctly.

## References

- [0xdf — Resource](https://0xdf.gitlab.io/2024/11/23/htb-resource.html)
- [IppSec — Resource](https://www.youtube.com/watch?v=ZIzxodu8axg)
- [Hack The Box — Resource](https://app.hackthebox.com/machines/resource)
