---
challenge: Artifact Of Dangerous Sighting
type: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, vhdx, ntfs, ads, powershell, evtx]
---

# Artifact Of Dangerous Sighting — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

A Windows VHDX image is provided. PowerShell history shows a file hidden in an Alternate Data Stream and commands that clear logs. Mount the image, read the ADS, recover System.evtx events and deobfuscate the script to reconstruct the flag.

## Statement and surface

- Forensics, Medium, retired.
- `2023-03-09T132449_PANDORA.vhdx`.
- The prompt says the user saw Event Viewer open.

```bash
file 2023-03-09T132449_PANDORA.vhdx
sha256sum 2023-03-09T132449_PANDORA.vhdx
```

## Reconnaissance

```bash
# Mount read-only
sudo mount -o ro,loop,offset=<OFFSET> image.vhdx /mnt/evidence
ls -la /mnt/evidence/Users
```

- The image contains the `Pandora` profile.
- `ConsoleHost_history.txt` shows `type finpayload > C:\Windows\Tasks\ActiveSyncProvider.dll:hidden.ps1`.
- Following commands clear PowerShell logs.

## Artifact analysis

`ActiveSyncProvider.dll` contains an alternate stream named `hidden.ps1`. List it with `dir /r` or `Get-Item -Stream *` and extract it with `Get-Content -Stream hidden.ps1`. The script is obfuscated with variables and concatenation to hide the URL and flag.

```powershell
Get-Item C:\Windows\Tasks\ActiveSyncProvider.dll -Stream *
Get-Content C:\Windows\Tasks\ActiveSyncProvider.dll -Stream hidden.ps1
```

## Finding explanation

The attacker used an ADS to hide the payload inside a legitimate DLL. PowerShell history proves execution and log clearing; `System.evtx` retains part of the activity. Deobfuscating the script reveals the flag path or value.

## Local reproduction

```bash
python3 -m pip install python-evtx
evtx_dump.py /mnt/evidence/Windows/System32/winevt/Logs/System.evtx | grep -i powershell
```

## Evidence

- PowerShell history with the ADS and `wevtutil cl`.
- Extracted `hidden.ps1` stream.
- System.evtx event showing execution.
- Flag redacted.

## Lessons learned

- ADS files are invisible to a normal `dir`.
- Clearing a log does not remove every artifact.
- PSReadline history is a high-value source.

## Mitigations and detection

- Audit ADS creation and PowerShell execution.
- Centralize logs before an attacker can clear them.
- Alert on `wevtutil cl` and `Remove-EventLog`.
- References: MITRE T1564.004, T1070.001, HTB Artifact Of Dangerous Sighting.

## References

- <https://www.hackthebox.com/challenges/Artifact%20Of%20Dangerous%20Sighting>
- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/artifact-of-dangerous-sighting/>
- <https://attack.mitre.org/techniques/T1564/004/>
- <https://attack.mitre.org/techniques/T1070/001/>
