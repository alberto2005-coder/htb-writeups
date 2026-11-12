---
machine: Search
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, credentials, wdigest, bloodhound, gmsa, sebackup]
---

# Search — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The corporate site leaks credentials in an image and grants domain access. Enumeration reveals `WDigest` enabled, a gMSA account and backup privileges; with them NTDS is dumped and the domain compromised.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p53,80,88,135,139,389,443,445,464,636,3268,5985 <IP>
```

Add `search.htb` to hosts. Enumerate vhosts, users and SMB resources. Site images may contain metadata or text with credentials.

## Initial access

Download the images and review metadata/OCR. A credential authenticates to the domain and grants SMB/WinRM access.

```bash
smbclient -L //<IP> -U '<user>%<password>'
```

## Lateral movement

Check the registry for cleartext credentials:

```powershell
reg query HKLM\\SYSTEM\\CurrentControlSet\\Control\\SecurityProviders\\WDigest
```

If `UseLogonCredential` is 1, a credential can be extracted from memory with `mimikatz`. Run BloodHound and identify paths to more privileged accounts, including a gMSA.

## Escalation to administrator

With `ReadGMSAPassword` or `SeBackupPrivilege`, obtain credential material. Dump `NTDS.dit` and extract hashes:

```powershell
secretsdump.py -just-dc -ntds ntds.dit -system SYSTEM <user>@<IP>
```

Use the administrator hash to access the DC and read the flag.

## Evidence

- Image with redacted credential.
- `WDigest` and BloodHound output.
- gMSA/backup and redacted NTDS dump.
- Administrator access.

## Lessons learned

- Images and metadata can leak credentials.
- Enabled `WDigest` exposes secrets in memory.
- BloodHound reveals hidden privilege paths.
- `SeBackupPrivilege` allows reading NTDS.

## Mitigation and detection

- Disable `WDigest` and protect LSASS.
- Audit gMSA and delegations.
- Restrict `SeBackupPrivilege`.
- Monitor access to `NTDS.dit` and tickets.

## References

- <https://www.hackthebox.com/machines/search>
- <https://bloodhound.readthedocs.io/>
- <https://attack.mitre.org/techniques/T1003/003/>
