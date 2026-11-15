---
machine: Chaos
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, wordpress, webmail, pdftex, rbash, password-reuse, privesc]
---

# Chaos — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Enumeration finds WordPress, Webmin and webmail. Weak credentials open the mailbox, where an encrypted message points to a secret URL with pdfTeX and `\write18` enabled, yielding a `www-data` shell. A shared password moves to `ayush`, `tar` escapes `rbash`, and the Firefox profile stores root's password, also reused on Webmin.

## Recon

```bash
nmap -Pn -sCV -p80,110,143,993,995,10000 <IP>
```

- `80` Apache with WordPress under `/wp/wordpress/` and a landing page.
- `10000` Webmin 1.890.
- `110`, `143`, `993` and `995` mail services; webmail is on a vhost.

## Enumeration

- `gobuster` finds `/source`, and WordPress allows user enumeration.
- A blog post contains webmail credentials.
- The mailbox has an encrypted message; decrypting it reveals a secret URL.
- `wfuzz` finds the webmail vhost and the `J00_w1ll_f1Nd_n07H1n9_H3r3` path.

## Foothold

The secret page compiles LaTeX with `pdfTeX` and `\write18` enabled. The `content` parameter goes to the compiler; `\immediate\write18{...}` runs commands.

```bash
curl -X POST -d 'content=%5Cimmediate%5Cwrite18%7Bid%7D&template=test3' \
  http://chaos.htb/J00_w1ll_f1Nd_n07H1n9_H3r3/ajax.php
```

A reverse shell gives `www-data`.

## Lateral movement

The shared password allows `su ayush`. His shell is `rbash`; `tar` with `--checkpoint-action=exec` or the `tar cf /dev/null` trick escapes it.

```bash
tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash
```

## Privilege escalation

`ayush`'s Firefox profile holds a master password and saved credentials. `firefox_decrypt.py` extracts a root password; it also works on Webmin.

```bash
python3 firefox_decrypt.py /home/ayush/.mozilla/firefox
su root
```

## Evidence

- WordPress, Webmin and webmail exposed.
- Weak credentials and an encrypted message.
- pdfTeX with `\write18`.
- `rbash` escaped with `tar`.
- Root password in Firefox, reused on Webmin.

## Lessons learned

- Mail and webmail services widen the credential surface.
- `pdfTeX` with `\write18` is direct command execution.
- `rbash` is not a jail when escape-capable binaries remain.
- Browser profiles store reusable secrets.

## Mitigation and detection

- Disable `\write18` and compile in a networkless sandbox.
- Never reuse passwords across mail, system and panels.
- Restrict `rbash` and audit `GTFOBins` binaries.
- Protect browser profiles and rotate shared credentials.

## References

- [0xdf — Chaos](https://0xdf.gitlab.io/2019/05/25/htb-chaos.html)
- [IppSec — Chaos](https://www.youtube.com/watch?v=no9UnySBQrU)
- [Hack The Box — Chaos](https://app.hackthebox.com/machines/chaos)
