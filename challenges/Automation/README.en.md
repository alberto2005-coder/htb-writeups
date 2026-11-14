---
challenge: Automation
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, powershell, obfuscation, base64]
---

# Automation — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

An obfuscated PowerShell script downloads and runs a second stage. Decode the base64, rebuild concatenated strings and follow the URL to the payload containing the flag.

## Prompt and surface

- Forensics, Easy, retired.
- A script or PowerShell artefact is provided.
- The prompt mentions automation.

```bash
file automation.ps1
head -40 automation.ps1
```

## Reconnaissance

- `-enc`/`-EncodedCommand`, `FromBase64String`, `IEX` and string concatenation.
- Randomised variable names.
- A URL or an extra blob.

## Code analysis

Extract the base64 and decode it as UTF-16LE. Deobfuscate the result by resolving variables and concatenations. The second stage usually downloads a binary or runs another string.

```powershell
[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($blob))
```

## Why it works

Obfuscation is not encryption: it only hides. The `DownloadString`/`IEX` flow can be reconstructed and the payload obtained without running it.

## Local reproduction

- Work in an isolated VM with no network.
- Disable automatic execution.
- Save each decoded stage to a separate file.
- Hash files before and after.

## Exploitation

```bash
python3 decode.py automation.ps1
strings -a stage2.bin | grep -i flag
```

The flag appears in the payload or output; it is redacted.

## Evidence

- Base64 blob and decoded script.
- Stage hashes.
- Redacted URL/C2.

## Lessons learned

- `IEX` and `DownloadString` are strong indicators.
- UTF-16LE is common in `EncodedCommand`.
- Static deobfuscation avoids running malware.

## Mitigations and detection

- Enable Script Block Logging (4104) and AMSI.
- Restrict PowerShell and sign scripts.
- Alert on `-enc`, `IEX` and PowerShell downloads.

## References

- <https://www.hackthebox.com/challenges/Automation>
- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/automation/>
- <https://attack.mitre.org/techniques/T1059/001/>
