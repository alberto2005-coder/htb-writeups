---
sherlock: EasyMoney
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware-analysis, windows, lnk, yandex, certutil]
---

# EasyMoney — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A user downloads an alleged money giveaway and runs a shortcut. Days later, the host shows persistence and C2 traffic. The user profile, PowerShell logs and downloaded files are provided.

## Evidence

- `2025-GiveAways.lnk` and its `customDestinations-ms`.
- PowerShell history and the `certutil` cache.
- `wldp.dll`, `yanda.tmp` and the `%LOCALAPPDATA%` tree.

```bash
sha256sum 2025-GiveAways.lnk
LECmd.exe -f 2025-GiveAways.lnk
```

## Investigation

### 1. Inventory and triage

`LECmd` shows the LNK points to PowerShell ISE and launches a command with a URL. The filename imitates a giveaway. Review downloads, prefetch and child processes to confirm execution.

```bash
JLECmd.exe -f customDestinations-ms --csv out
```

### 2. Timeline

The LNK runs PowerShell, which enumerates packages and downloads a DLL with `certutil`. The DLL is placed next to a Yandex browser vulnerable to DLL search order. When the browser opens, `wldp.dll` loads the payload and establishes C2.

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational'
```

### 3. Key artifact

The `CryptnetUrlCache` keeps the downloaded binary. The mutex name and `yanda.tmp` path appear in executable analysis. Together they confirm sideloading and the C2 framework.

## Conclusions

- Initial access was a phishing LNK.
- `certutil` downloaded the malicious DLL.
- Yandex sideloading executed the payload.
- The C2 and mutex are high-confidence IOCs.

## Lessons

- LNKs can launch PowerShell without a visible executable.
- `certutil` remains a download LOLBin.
- The cryptography cache keeps downloaded files.
- Sideloading abuses a legitimate application.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/luckystars0612/Sherlock-HTB/tree/main/EasyMoney>
- <https://attack.mitre.org/techniques/T1204/002/>
