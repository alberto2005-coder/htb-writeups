---
sherlock: "AoTR 1: A Call from the Museum"
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, email, lnk, powershell, registry]
---

# AoTR 1: A Call from the Museum — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A museum employee receives an email about an international exhibition and opens an attachment. Soon after, the workstation shows anomalous activity. The email and user artifacts are provided to reconstruct initial access.

## Evidence

- `URGENT_Updated_Health_&_Customs_Compliance_for_Cross-Border_Festive_Event.eml`.
- A `.lnk` shortcut and a PowerShell script.
- `NTUSER.DAT` hive and files under `%TEMP%`.

```bash
sha256sum *.eml *.lnk
file *
```

## Investigation

### 1. Inventory and triage

Review email headers: sender, `Return-Path`, `Message-ID`, servers and links. The attachment is a LNK posing as a PDF and pointing to a legitimate executable with controlled arguments.

```bash
head -40 urgent.eml
exiftool urgent.eml
```

### 2. Timeline

The LNK runs and launches PowerShell with an encoded string. The script reads the registry `MachineGuid`, sends data to a domain and downloads a second stage. Sort artifacts by time and identify the first malicious process.

```powershell
Get-Content .\script.ps1
```

### 3. Key artifact

`HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid` appears in the script and identifies the victim host. The C2 domain and second payload path emerge after deobfuscating the concatenated strings.

## Conclusions

- Initial access was a malicious LNK delivered by email.
- PowerShell was used for reconnaissance and download.
- `MachineGuid` served as the victim identifier.
- Block the C2 and hunt for the second payload on other hosts.

## Lessons

- LNK files can masquerade as documents.
- PowerShell history and registry complement email analysis.
- An `.eml` preserves headers and attachments.
- Newly registered domains are a useful indicator.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://medium.com/@annisaep/hack-the-box-aotr-a-call-from-the-museum-write-up-457926888768>
- <https://attack.mitre.org/techniques/T1204/002/>
