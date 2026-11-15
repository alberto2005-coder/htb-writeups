---
machine: Forgot
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, host-header, cache-poisoning, pickle, privesc]
---

# Forgot — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The reset form builds the link from the `Host` header, so a victim receives a link to the attacker and `robert`'s token is stolen. Then a Varnish cache flaw serves the administrator session and exposes a ticket with `diego` credentials. `diego` can run a security script as root that loads `.sav` models with `pickle`, enabling code execution.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 20.04 and `80/tcp` serving a Flask site.
- The `forgot.htb` vhost has login, registration and password reset.
- Varnish caches `/static` responses and the server uses Werkzeug.

## Enumeration

- The `robert-dev-<number>` user is valid and the reset link is generated dynamically.
- Changing `Host` to the attacker IP makes the reset link point there.
- Varnish can cache an authenticated page when the right `Host` and path are forced.

## Foothold

Request a reset for `robert-dev-<number>` with `Host: <ATTACKER>` and capture the token. Change the password, log in as Robert and send a reset link to the administrator. The authenticated admin response is cached and recovered; it contains a ticket with `diego` credentials.

```bash
python3 -m http.server 80
# POST /forgot with Host: <ATTACKER>
# GET /reset?token=... on the attacker server
ssh diego@forgot.htb
```

## Lateral movement

`diego` has SSH access and can enumerate local scripts. The ticket and cache already provided the jump from the web; the next step is the privileged script.

## Privilege escalation

`sudo -l` allows `/opt/security/ml_security.py`. The script loads `.sav` models with `pickle.load` from `/opt/security/lib`. Replace one model with a malicious pickle; when run as root, the payload creates a SUID shell or runs a command.

```bash
sudo -l
ls -l /opt/security/lib
# replace a .sav with a pickle using a malicious __reduce__
sudo /opt/security/ml_security.py
```

## Evidence

- Reset token captured with a malicious `Host`.
- Cached admin session and ticket with `diego` credentials.
- Replaced `.sav` model and root execution.

## Lessons learned

- Reset links must not be built from the `Host` header.
- Caches can mix authenticated responses between users.
- `pickle` on external models or data is code execution.

## Mitigation and detection

- Fix the reset domain in configuration and validate `Host`.
- Do not cache authenticated responses; use `Cache-Control: private`.
- Sign or validate models and avoid `pickle` with writable files.

## References

- [0xdf — Forgot](https://0xdf.gitlab.io/2023/03/04/htb-forgot.html)
- [IppSec — Forgot](https://www.youtube.com/watch?v=wKcTELVst20)
- [Hack The Box — Forgot](https://app.hackthebox.com/machines/forgot)
