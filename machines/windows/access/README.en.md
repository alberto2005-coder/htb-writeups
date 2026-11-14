---
machine: Access
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, ftp, mdb, outlook, telnet, runas, dpapi]
---

# Access — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Anonymous FTP provides `backup.mdb` and a protected ZIP. The Microsoft Access database contains `engineer`'s password, which opens the ZIP and reveals an Outlook PST with `security`'s password; telnet allows login. On the host, `cmdkey /list` shows cached Administrator credentials and `runas /savecred` runs a reverse shell with those privileges.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p21,23,80 <IP>
ftp -a <IP>
```

## Enumeration

- IIS on 80, anonymous FTP on 21 and telnet on 23.
- `Backups/backup.mdb` and `Engineer/Access Control.zip` are accessible.
- The database contains the `auth_user` table with credentials.

## Initial access

Download the MDB and export `auth_user` with `mdb-export`; `engineer`'s password opens the ZIP, which contains `Access Control.pst`. Reading the email provides `security`'s password, valid over telnet, and a shell is obtained.

## Privilege escalation

`cmdkey /list` reveals stored Administrator credentials. Upload a Nishang reverse shell and run it with `runas /savecred /user:ACCESS\Administrator`, inheriting the cached credentials. Alternatively, extract the DPAPI master key and credential file and decrypt them offline.

## Evidence

- FTP listing with both files.
- `mdb-export` output and the PST email.
- `cmdkey /list` and a shell as Administrator.

## Lessons learned

- A database backup can hold credentials for several systems.
- PST files and email are a classic source of secrets.
- Cached Windows credentials allow lateral movement without the password.

## Mitigation and detection

- Disable anonymous FTP and telnet; use SFTP/SSH.
- Protect backups and mailboxes with encryption and least privilege.
- Clear Credential Manager and apply LAPS to local accounts.

## References

- [0xdf — Access](https://0xdf.gitlab.io/2019/03/02/htb-access.html)
- [IppSec — Access](https://www.youtube.com/watch?v=Rr6Oxrj2IjU)
- [Hack The Box — Access](https://app.hackthebox.com/machines/access)
