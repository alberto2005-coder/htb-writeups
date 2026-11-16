---
machine: CTF
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, ldap-injection, otp, second-order, 7z, privesc]
---

# CTF — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site authenticates with LDAP, a username and an OTP. Double-URL-encoded LDAP injection leaks the username and token seed; `stoken` generates the OTP and a second-order injection bypasses the check. `page.php` source leaks `ldapuser`'s password, and a `7za` wildcard backup reads root's flag.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with PHP 5.4 on CentOS 7.
- The landing page warns about a temporary ban for too many 404s.
- `/status.php` shows status and blocked IPs; login asks for username and OTP.

## Enumeration

The login HTML reveals the token is stored in an existing LDAP attribute. Double-encode `*` as `%252a`; the username starts with `l` and can be extracted character by character. Then enumerate candidate attributes (`mail`, `pager`, `userPassword`) and leak the OTP seed with `ldapuser)(<ATTR>=<value>*`.

## Foothold

With the seed and the server time offset, `stoken` generates the OTP. The first login reaches `page.php`, but the command is rejected; log in again with `ldapuser)))%00` for a second-order injection that bypasses the check. The page source downloads in base64 and contains `$password` for SSH.

```bash
# LDAP login with double encoding and OTP
curl -s http://<IP>/login.php --data 'inputUsername=ldapuser%2529%2529%2529%2500&inputOTP=<OTP>'
# backup wildcard
touch @list; ln -fs /root/root.txt list
```

## Lateral movement

There is no extra pivot: `ldapuser` logs in over SSH and the next target is the root backup script.

## Privilege escalation

`/backup/backup.sh` runs `7za a /backup/$filename.zip -t7z -snl -p$pass -- *` every minute. In the writable directory create `@list` and a `list` symlink to `/root/root.txt`; `7za` treats `@list` as a file list and the error includes the target contents. You can also follow the log with `tail -f` before the script clears it.

## Evidence

- Username and OTP seed extracted through LDAP injection.
- `stoken` and second-order login.
- Password in `page.php` source.
- `7za` wildcard backup and root read.

## Lessons learned

- Double encoding can bypass LDAP character filters.
- Storing the OTP in a readable attribute increases impact.
- A two-stage user check can be injectable in the second stage.
- Wildcards in root scripts turn filenames into arguments.

## Mitigation and detection

- Parameterize LDAP queries and escape metacharacters.
- Do not reuse existing attributes for secrets.
- Avoid wildcards; use `find -print0` and `xargs -0`.
- Watch for `@*` files and `7za` errors in backups.

## References

- [0xdf — CTF](https://0xdf.gitlab.io/2019/07/20/htb-ctf.html)
- [IppSec — CTF](https://www.youtube.com/watch?v=51JQg202csw)
- [Hack The Box — CTF](https://app.hackthebox.com/machines/ctf)
