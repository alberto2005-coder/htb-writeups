---
machine: Minion
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, icmp, ssrf, powershell, ads]
---

# Minion — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site on 62696 has a `test.asp` that makes server-side requests and a `/backend` panel with command execution. The only egress is ICMP, so a Python/PowerShell shell is built over pings. A scheduled task runs a writable PowerShell script; it is hijacked to become `decoder.MINION`. A backup with an alternate data stream stores the Administrator password.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
62696/tcp http  Microsoft IIS 8.5
80/tcp    http  internal only
5985/tcp  winrm internal
```

## Enumeration

- `robots.txt` points to `/backend`, an ASP panel with command execution.
- `test.asp?u=` makes server-side requests (SSRF).
- SSRF scanning finds 80, 5985 and 47001 on localhost.
- Internet egress only allows ICMP.

## Foothold

A `cmd.aspx` is uploaded through the panel and `whoami` runs. With no TCP reverse shell, a Python/Scapy script sends commands in ICMP packets and receives output the same way; on the host, a PowerShell block runs the command and splits the response.

```text
test.asp?u=http://127.0.0.1:80/
POST /cmd.aspx  xcmd=whoami
```

## Lateral movement

ICMP enumeration finds a scheduled task running a PowerShell script from a writable path. The script is replaced with one that adds a user or runs a shell, and the task launches it as `decoder.MINION`.

```powershell
schtasks /query /fo LIST /v
```

## Privilege escalation

A backup ZIP contains an NTFS alternate data stream with the Administrator password. It is read with `Get-Content -Stream` or from Linux with `ntfs-3g`/`7z`. Those credentials open WinRM or `runas` and yield Administrator.

```powershell
Get-Item .\backup.zip -Stream *
Get-Content .\backup.zip -Stream <STREAM>
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- SSRF reaches services bound to localhost.
- ICMP can be a full C2 channel when it is the only egress.
- Scheduled tasks running writable scripts are a classic hijack.
- NTFS alternate data streams hide data from basic enumeration.

## Mitigations and detection

- Remove `test.asp` and restrict the `/backend` panel.
- Filter egress and do not allow arbitrary ICMP.
- Protect scheduled-task scripts and review their ACLs.
- Scan alternate data streams and keep passwords out of backups.

## References

- [0xdf — Minion](https://0xdf.gitlab.io/2022/04/07/htb-minion.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+minion)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+minion+writeup)
