---
title: ADIDNS — name hijacking with CREATE_CHILD
tags: [windows, active-directory, dns, adidns, responder, mitm]
---

# ADIDNS — name hijacking with CREATE_CHILD

[🇪🇸 Español](adidns-record-spoofing.md) | **English**

## Concept

AD-integrated DNS zones are stored as objects in the directory. By default, authenticated users can create child records (`CREATE_CHILD`) under many names. If a service tries to resolve a name that does not exist yet, an attacker can create it pointing to their own IP and win resolution.

## When it applies

- There is an AD forest with AD-integrated DNS.
- A linked server, application or script resolves a nonexistent name.
- The compromised user can create records in the zone.

## Procedure

1. Enumerate the zone and permissions with `Powermad` or `dnstool.py`.
2. Find a name the victim resolves that does not exist.
3. Create an A record pointing to the attacker IP.
4. Listen with Responder or your own server and capture authentication.

```powershell
Import-Module .\Powermad.ps1
Get-ADIDNSNode -DomainController dc.htb -Zone htb
New-ADIDNSNode -DomainController dc.htb -Zone htb -Node fake -Data 10.10.14.9 -Type A
```

```bash
python3 dnstool.py -u 'HTB\user' -p '<PASSWORD>' -r fake.htb -a add -t A -d 10.10.14.9 dc.htb
```

## Variants

- Create a wildcard record (`*`) to capture any unresolved name.
- Use `TXT` or `CNAME` to redirect to another host.
- Chain with `PetitPotam` or `xp_dirtree` to force authentication.

## Limitations

- The `CREATE_CHILD` permission must exist; it is common on `Authenticated Users`, but not universal.
- The victim must resolve the name after it is created.
- Responder only captures legacy protocols (LLMNR, NBT-NS, mDNS); SMB needs relay or a fake server.

## Mitigation and detection

- Restrict `CREATE_CHILD` on sensitive zones and names.
- Audit events 5137, 5141 and DNS record changes.
- Use signed DNS and monitor new records pointing to external IPs.
- Stop internal services from resolving nonexistent names.

## References

- <https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-zones-records>
- <https://github.com/Kevin-Robertson/Powermad>
- <https://attack.mitre.org/techniques/T1557/>
