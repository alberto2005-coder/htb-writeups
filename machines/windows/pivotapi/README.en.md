---
machine: PivotAPI
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, mssql, reversing, laps, asrep]
---

# PivotAPI — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A PDF on anonymous FTP leaks a username; AS-REP Roasting gives the first account. Reversing an obfuscated binary reveals MSSQL credentials, used as a tunnel to WinRM. An ACL chain and LAPS close the domain.

## Reconnaissance

```bash
nmap -Pn -sCV -p21,80,1433,3389,5985 <IP>
ftp <IP>
exiftool document.pdf | grep -i author
GetNPUsers.py <DOMAIN>/ -usersfile users.txt -no-pass -dc-ip <DC>
# Reversing
ilspycmd app.exe > app.cs
# MSSQL
mssqlclient.py <USER>@<IP> -windows-auth
bloodhound-python -u <USER> -p "<PASS>" -d <DOMAIN> -c All
```

## Enumeration

- Anonymous FTP with documents and metadata.
- Users without Kerberos preauthentication and exposed MSSQL.
- Obfuscated binary with credentials and LAPS permissions in AD.

## Initial access

`exiftool` on the PDF reveals a user. `GetNPUsers.py` obtains a crackable AS-REP and the password grants portal access. Analyze the binary with Procmon/ILSpy and recover MSSQL credentials.

## Privilege escalation

Use MSSQL as a pivot to run commands and reach WinRM. BloodHound shows permissions to read LAPS; recover the local administrator password and use it for DCSync or DC access.

## Evidence

- PDF metadata with the user.
- Cracked AS-REP and initial access.
- MSSQL query, WinRM tunnel and LAPS password.

## Lessons learned

- Document metadata leaks accounts.
- MSSQL can be a pivot and an execution path.
- LAPS read permissions equal local credentials.

## Mitigation and detection

- Clean metadata and restrict anonymous FTP.
- Require Kerberos preauthentication and limit MSSQL.
- Audit who can read LAPS and enforce least privilege.

## References

- [0xdf — PivotAPI](https://0xdf.gitlab.io/2021/11/06/htb-pivotapi.html)
- [Microsoft — LAPS](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview)
- [Hack The Box — PivotAPI](https://app.hackthebox.com/machines/pivotapi)
