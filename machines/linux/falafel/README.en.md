---
machine: Falafel
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, sqli, type-juggling, magic-hash, debugfs]
---

# Falafel — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The login uses loose comparisons and a magic hash logs in as admin. File upload yields a shell; escalation reads the screen from `/dev/fb0` and uses `debugfs` on the disk to reach root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
sqlmap -u "http://falafel.htb/login.php" --data="username=admin&password=test" --batch
# Magic hash for the bypass
curl -d "username=admin&password=240610708" http://falafel.htb/login.php
# After the shell
id; groups
cat /dev/fb0 > /tmp/fb.raw
debugfs -R "cat /root/root.txt" /dev/sdb1
```

## Enumeration

- PHP login with loose hash comparison.
- Upload form and a user-management application.
- The user belongs to groups with access to block devices.

## Initial access

Password `240610708` produces an MD5 hash starting with `0e`, and the comparison treats it as zero. Log in as admin, upload a PHP file and obtain execution as `www-data`.

## Privilege escalation

The application shows another user's credentials. With that account, read `/dev/fb0` to recover the screen and a password; the disk group allows `debugfs` on the partition and reading root files.

## Evidence

- Magic hash accepted by the login.
- PHP upload and shell as `www-data`.
- `/dev/fb0` read and `debugfs` on the disk.

## Lessons learned

- `==` comparisons with hashes can collapse to zero.
- Accessible block devices are equivalent to root.
- On-screen information can contain secrets.

## Mitigation and detection

- Use `password_verify` and strict comparisons.
- Restrict access to `/dev/fb0` and block devices.
- Validate upload extensions and permissions.

## References

- [0xdf — Falafel](https://0xdf.gitlab.io/2018/06/23/htb-falafel.html)
- [PHP — Type juggling](https://www.php.net/manual/en/language.types.type-juggling.php)
- [Hack The Box — Falafel](https://app.hackthebox.com/machines/falafel)
