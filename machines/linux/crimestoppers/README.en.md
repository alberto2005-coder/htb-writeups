---
machine: CrimeStoppers
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, lfi, php-filter, zip-wrapper, apache-module, privesc]
---

# CrimeStoppers — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An LFI in `?op=` reads source through `php://filter` and includes an uploaded ZIP through `zip://`, giving RCE as `www-data`. `dom`'s Thunderbird profile contains her password and moves to that user. A modified Apache module (`rootme`) runs commands as root when it receives a specific request.

## Recon

```bash
nmap -Pn -sCV -p80 <IP>
```

- Only `80` Apache 2.4.25 on Ubuntu 17.04.
- The site is an FSociety gallery with `/uploads` and `/upload.php`.
- `gobuster` finds `index.php?op=`, `upload.php` and `uploads/`.

## Enumeration

The `op` parameter is concatenated with `.php`. `php://filter` returns the source in base64.

```bash
curl -s 'http://<IP>/?op=php://filter/convert.base64-encode/resource=home' | base64 -d
```

The code shows uploads go to `uploads/<IP>/` with a random name and that `op` is included without validation.

## Foothold

Upload a ZIP with a `shell.php`; the `zip://` wrapper includes and runs it.

```text
?op=zip://uploads/<IP>/<FILE>.zip#shell.php&cmd=id
```

The shell runs as `www-data`.

## Lateral movement

`/home/dom` has a Mozilla/Thunderbird profile. `mozilla2john.py` extracts the `key3.db` hash; the master password is empty. Opening the profile recovers `dom`'s password, which works with `su`.

```bash
python3 mozilla2john.py key3.db > key3.hash
john key3.hash
su dom
```

## Privilege escalation

The `apache_modrootme` module is loaded in Apache and modified to run commands as root. `dom`'s mail documents the backdoor and the request that triggers it; sending it yields a root shell.

```bash
apachectl -M | grep rootme
```

## Evidence

- LFI with `php://filter` and source code.
- Uploaded ZIP included through `zip://`.
- Thunderbird profile and `dom`'s password.
- `rootme` Apache module and root.

## Lessons learned

- `php://filter` turns an LFI into source disclosure.
- `zip://` and `phar://` wrappers extend an LFI to execution.
- Mail profiles store system credentials.
- A malicious Apache module is persistence and root.

## Mitigation and detection

- Never include user-controlled paths; use allowlists.
- Disable unnecessary wrappers and validate uploads.
- Protect mail profiles and never reuse passwords.
- Verify Apache modules against official packages.

## References

- [0xdf — CrimeStoppers](https://0xdf.gitlab.io/2018/06/03/htb-crimestoppers.html)
- [IppSec — CrimeStoppers](https://www.youtube.com/watch?v=bgKth1K44QA)
- [Hack The Box — CrimeStoppers](https://app.hackthebox.com/machines/crimestoppers)
