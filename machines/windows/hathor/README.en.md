---
machine: Hathor
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, web, mojoportal, applocker, dll, certificate, dcsync, kerberos, privesc]
---

# Hathor — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

mojoPortal accepts the default `admin@admin.com` / `<PASSWORD>` credentials; a webshell is uploaded and copied to `.aspx` to get a shell as `web`. From `web`, the `Get-bADpasswords` CSV files are read and `BeatriceMill`'s hash is obtained; since NTLM is disabled, Kerberos (`kinit`) is used for SMB access. The share allows overwriting `7-zip64.dll`, which the `Bginfo64.exe` task loads and which yields a shell as `GinaWild`; from that account, `Bginfo64.exe` is taken over and replaced for a second shell. A code-signing certificate in the recycle bin signs a modified `Get-bADpasswords.ps1`, which runs as `bpassrunner`; its replication rights allow DCSync, and Administrator's hash provides a Kerberos ticket and an elevated shell.

## Reconnaissance

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985 <IP>
```

- `53`, `88`, `389`, `636`, `3268` and `3269`: DNS, Kerberos and LDAP on a domain controller.
- `80`: IIS with mojoPortal.
- `445`: SMB, central to the DLL chain and the shares.
- `5985`: WinRM.

```bash
echo '<IP> hathor.windcorp.htb' | sudo tee -a /etc/hosts
```

## Enumeration

The site is mojoPortal. Its default portal credentials log in as administrator. The panel allows uploads and validates the extension weakly: a webshell is uploaded with an allowed extension and copied to `.aspx` so IIS executes it.

Execution is constrained by AppLocker and Windows Firewall. Process, share and policy enumeration shows which binaries and DLLs are allowed and which share a scheduled task uses.

## Foothold

mojoPortal allows a webshell to be uploaded with an allowed extension and copied to `.aspx`; the result is a shell as `web`. The `share` share contains `AutoIt3_x64.exe`, `Bginfo64.exe`, the `7-zip64.dll` library and scripts. A task runs `Bginfo64.exe` every few minutes and loads the DLL from a writable path; AppLocker allows both binaries. From `web`, `C:\Get-bADpasswords\Accessible\CSVs` is also readable. The share is exploited during lateral movement, once SMB access is obtained.

```text
\\<HOST>\share\7-zip64.dll  → loaded by the scheduled process
\\<HOST>\share\Bginfo64.exe → execution allowed by AppLocker
```

## Lateral movement

`web` reads the CSVs in `C:\Get-bADpasswords\Accessible\CSVs` and obtains `BeatriceMill`'s hash, which is cracked. Since NTLM is disabled, `kinit beatricemill` requests a Kerberos ticket and `smbclient -k` accesses the `share` share. `7-zip64.dll` is overwritten there; when the task runs `Bginfo64.exe`, the DLL runs as `GinaWild` and returns a shell. `GinaWild` is in `ITDep` and can take ownership of `Bginfo64.exe`; it is replaced with `nc64.exe` and the task launches a second shell as `GinaWild`.

The public desktop has a `bAD Passwords.lnk` shortcut pointing to `C:\Get-bADpasswords\run.vbs`; the script creates an event and runs under a privileged account. `GinaWild`'s recycle bin holds `.pfx` certificates; one is a code-signing certificate. It signs a modified `Get-bADpasswords` script, so when it runs as `bpassrunner` it launches a controlled action.

## Privilege escalation

As `bpassrunner`, the script's collected information and replication rights are accessible. `Get-ADReplAccount` against the domain controller retrieves Administrator's hash. Since NTLM is disabled, the hash is not used directly: `getTGT.py` requests a TGT and the Kerberos cache provides the elevated shell.

```powershell
Get-ADReplAccount -SamAccountName administrator -Server 'hathor.windcorp.htb'
```

```bash
getTGT.py -hashes :<NTHASH> windcorp.htb/administrator
KRB5CCNAME=./administrator.ccache evil-winrm -i hathor.windcorp.htb -r WINDCORP.HTB
```

## Evidence

- mojoPortal login with default credentials.
- Webshell copied to `.aspx` and executed despite AppLocker.
- DLL and EXE overwritten in the share and a shell as `GinaWild`.
- Cracked `BeatriceMill` hash and SMB access over Kerberos.
- `.pfx` certificate recovered from the recycle bin and signed script.
- Execution as `bpassrunner` and DCSync.
- Kerberos ticket and a shell as Administrator.

## Lessons learned

- Changing default portal credentials is mandatory.
- AppLocker and the firewall reduce impact but do not stop abuse of allowed binaries and DLLs.
- A writable share used by scheduled tasks is code execution.
- Code-signing certificates in the recycle bin sign payloads as legitimate software.
- DCSync works even with NTLM disabled; Kerberos is the alternative.

## Mitigations and detection

- Change default credentials and enforce MFA on administrative portals.
- Restrict file uploads and validate extension and content server-side.
- Apply AppLocker/WDAC with path and signature rules and review exceptions.
- Do not grant users write access to shares holding DLLs or EXEs run by tasks.
- Protect code-signing certificates and revoke those that reach the recycle bin.
- Monitor DCSync, `Get-bADpasswords`, ticket creation and signed script execution.

## References

- [0xdf — Hathor](https://0xdf.gitlab.io/2022/11/19/htb-hathor.html)
- [IppSec — Hathor](https://www.youtube.com/watch?v=yweDaXZdt4s)
- [Hack The Box — Hathor](https://app.hackthebox.com/machines/hathor)
- [Knowledge — Get-bADpasswords and DCSync](../../../knowledge/windows/badpasswords-dcsync.en.md)
