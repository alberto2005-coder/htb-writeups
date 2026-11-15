---
machine: Coder
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, smb, dotnet, keepass, teamcity, adcs, certifried]
---

# Coder — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An SMB share holds a .NET executable and an encrypted file. Reverse engineering reveals the encryption flaw and recovers a KeePass database and keyfile, with TeamCity credentials and a 2FA backup. The Chrome plugin is reversed to recover the TOTP seed, the CI/CD pipeline gives a shell and a diff leaks `e.black` credentials. With PKI Admins, a template without the security extension is created and Certifried (CVE-2022-26923) is exploited to obtain the DC and Administrator.

## Recon

```bash
nmap -Pn -sCV -p53,88,139,389,445,5985,9389 <IP>
```

- The host is a domain controller for `coder.htb`.
- SMB, LDAP, Kerberos and WinRM are open.
- `netexec smb <IP> -u guest -p '' --shares` shows a development share.

## Enumeration

- The share contains `Coder.exe`, `Coder.enc` and build notes.
- `dotPeek` shows the encryption algorithm and a key derived from a fixed value.
- Decrypting `Coder.enc` yields a KeePass database and keyfile.

```bash
smbclient //<IP>/Development -N
dotpeek Coder.exe
kpcli --kdb coder.kdbx --key coder.key
```

## Foothold

The database contains `svc_teamcity` credentials and a 2FA backup. The Chrome plugin that creates the backup can be reversed: the TOTP seed is encrypted with a weak password, which cracks. The 6-digit code opens TeamCity.

```bash
hashcat -m 16500 backup.hash rockyou.txt
```

## Lateral movement

As a user with build rights, create a branch with a diff that runs commands in the pipeline. The agent runs as `svc_teamcity` and can read `C:\ProgramData\JetBrains\TeamCity\system\changes`. An old diff contains `Get-ADCS_Report.ps1`, `key.key` and `enc.txt`; the script decrypts `e.black`'s password.

```powershell
Get-ChildItem C:\ProgramData\JetBrains\TeamCity\system\changes
```

## Privilege escalation

`e.black` is in `PKI Admins` and can import AD CS templates. Create a template with `CT_FLAG_NO_SECURITY_EXTENSION` and, as `s.blade`, add a computer to the `BuildAgents` OU with `dNSHostName` set to the DC. Enroll the computer with the template, obtain a certificate as the DC and run `secretsdump`. The Administrator hash opens WinRM.

```bash
certipy-ad template -u e.black@coder.htb -p '<PASSWORD>' -dc-ip <DC> -template ESC1 -no-security-extension
certipy-ad req -u 'DC01$'@coder.htb -p '<MACHINE_PASSWORD>' -ca coder-DC01-CA -template ESC1 -dc-ip <DC>
certipy-ad auth -pfx dc01.pfx -dc-ip <DC>
```

## Evidence

- SMB share with .NET binary and encrypted file.
- KeePass database with keyfile and TeamCity credentials.
- 2FA backup and recovered TOTP seed.
- CI/CD pipeline and diff with `e.black` credentials.
- AD CS template and Certifried to Administrator.

## Lessons learned

- Reverse engineering an encryption binary can reveal the key.
- An unprotected 2FA backup is as good as losing the second factor.
- CI/CD pipelines are remote execution and their artifacts leak secrets.
- Certifried survives when a template omits the security extension.

## Mitigation and detection

- Do not store secrets in development shares or build artifacts.
- Protect TOTP backups with strong passwords and isolated storage.
- Audit AD CS templates and block `CT_FLAG_NO_SECURITY_EXTENSION`.
- Review computer creation with a DC `dNSHostName` and changes to `PKI Admins`.

## References

- [0xdf — Coder](https://0xdf.gitlab.io/2023/12/16/htb-coder.html)
- [IppSec — Coder](https://www.youtube.com/watch?v=uZiEKiG96VI)
- [Hack The Box — Coder](https://app.hackthebox.com/machines/coder)
