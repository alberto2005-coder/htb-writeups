---
machine: Undetected
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, phpunit, cve-2017-9841, apache, backdoor, sshd, reversing, privesc]
---

# Undetected — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `store.djewelry.htb` vhost exposes `vendor/composer/installed.json`, revealing PHPUnit 5.6.2. `eval-stdin.php` allows unauthenticated PHP execution (CVE-2017-9841) and gives `www-data`. A binary in `/var/backups` shows a previous attacker added `*1` users to `/etc/passwd` and `/etc/shadow`; crack the hash to get `steven1`. The Apache module `mod_reader.so` downloads a backdoored sshd with an XOR password, which reverses to root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.2 and `80` Apache 2.4.41 on Ubuntu 20.04.
- `index.php` returns 404; `index.html` is the landing page.
- The `store.djewelry.htb` vhost is found through subdomain fuzzing.

## Enumeration

`/vendor/composer/installed.json` lists dependencies and confirms PHPUnit 5.6.2. Searching the version finds CVE-2017-9841: `vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php` evaluates the POST body.

## Foothold

Send `<?php system("id"); ?>` to the endpoint and confirm execution. A base64 reverse shell avoids character issues and returns `www-data`. `/var/backups` has an `info` binary that, when reversed, shows a previous attacker added `<user>1` users with duplicate UID and a fixed hash to `/etc/shadow`.

```bash
# PHPUnit
curl 'http://store.djewelry.htb/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php' \
  -d '<?php system("id"); ?>'
# hash and sshd
hashcat -m 1800 steven1.hash rockyou.txt
python3 backdoor_sshd.py
ssh root@<IP>
```

## Lateral movement

The `steven1` user already exists with the same UID as `steven`. Crack the `/etc/shadow` hash with hashcat mode 1800 and the password logs in as `steven1`, not `steven`.

## Privilege escalation

`/usr/lib/apache2/modules/mod_reader.so` and `reader.load` were modified by the attacker. The module runs `wget` from `sharefiles.xyz/image.jpeg` over `/usr/sbin/sshd`; the resulting binary has a backdoor in `auth_password` comparing the password with 31 bytes XOR 0x96. Extract the bytes, reverse the XOR and log in as root.

## Evidence

- `installed.json` with PHPUnit 5.6.2.
- `eval-stdin.php` and `www-data` shell.
- `*1` users and `steven1` hash.
- `mod_reader.so` and sshd with XOR password.

## Lessons learned

- Development dependencies should not remain in production.
- A backup binary can document the previous attack.
- Duplicate-UID users hide backdoors.
- Apache modules and modified binaries survive superficial cleanup.

## Mitigation and detection

- Remove development `vendor` and block `eval-stdin.php`.
- Audit `/etc/passwd`, `/etc/shadow` and duplicate UIDs.
- Verify Apache modules and system binaries.
- Monitor downloads and changes to `/usr/sbin/sshd`.

## References

- [0xdf — Undetected](https://0xdf.gitlab.io/2022/07/02/htb-undetected.html)
- [IppSec — Undetected](https://www.youtube.com/watch?v=TNwZAacbQs4)
- [Hack The Box — Undetected](https://app.hackthebox.com/machines/undetected)
