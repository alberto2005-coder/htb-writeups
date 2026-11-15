---
machine: Previse
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, execute-after-redirect, command-injection, hashcat, path-hijack, privesc]
---

# Previse — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An execute-after-redirect allows access to `accounts.php` without a session and creates a user. The downloaded source reveals command injection in `logs.php`, giving `www-data`. The database leaks hashes and one cracks to `m4lwhere`; `/opt/scripts/access_backup.sh` runs as root and calls `gzip` without an absolute path, allowing a path hijack.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with `previse.htb`.
- The site has login, registration and a management menu.
- `gobuster` finds `accounts.php`, `logs.php`, `download.php` and `status.php`.

## Enumeration

`accounts.php` returns a 302 without a session but keeps executing after sending the redirect. Intercept the response, change 302 to 200 to see the form, create a user and log in.

## Foothold

With a session, download source from `download.php`. `logs.php` passes `delim` unsanitized to `exec()`:

```php
$output = exec("/usr/bin/python /opt/scripts/log_process.py {$_POST['delim']}");
```

Inject `; bash -c '...'` and get `www-data`.

## Lateral movement

`config.php` holds MySQL credentials. Dump the `accounts` hashes and crack `m4lwhere`'s; the password is reused on the system.

```bash
hashcat -m 500 hashes.txt rockyou.txt
ssh m4lwhere@previse.htb
```

## Privilege escalation

`m4lwhere` can run `/opt/scripts/access_backup.sh` as root. The script calls `gzip` without an absolute path and `/dev/shm` is writable. Place a malicious `gzip`, prepend `/dev/shm` to `PATH` and run the script.

```bash
export PATH=/dev/shm:$PATH
sudo /opt/scripts/access_backup.sh
```

## Evidence

- EAR in `accounts.php`.
- Injection in `logs.php` and `www-data`.
- MySQL hashes and `m4lwhere`.
- `access_backup.sh`, `gzip` and root.

## Lessons learned

- `header("Location")` without `exit` does not stop execution.
- `exec()` with user input is direct injection.
- Database hashes are reused on the system.
- A root script with relative binaries is path hijack.

## Mitigation and detection

- Terminate execution after a redirect.
- Use `escapeshellarg` and allowlists.
- Unique hashes and separate passwords.
- Use absolute paths and a safe `PATH` in root scripts.

## References

- [0xdf — Previse](https://0xdf.gitlab.io/2022/01/08/htb-previse.html)
- [IppSec — Previse](https://www.youtube.com/watch?v=LI9mw1rMKVw)
- [Hack The Box — Previse](https://app.hackthebox.com/machines/previse)
