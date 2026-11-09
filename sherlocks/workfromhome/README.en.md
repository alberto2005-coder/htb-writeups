---
sherlock: WorkFromHome
domain: DFIR / Windows
difficulty: Medium
platform: Hack The Box
evidence: Laptop artifacts after credential theft and RDP intrusion
tools: [KAPE, MFTECmd, Timeline Explorer, Eric Zimmerman tools]
---

# WorkFromHome — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

A remote employee falls for a **phishing site** impersonating the corporate login and hands over credentials. The attacker enters over **RDP**, abuses a volume-management privilege, drops a **malicious DLL** and keeps persistence by hijacking the **WMI** flow.

## Evidence

- User profile: browser history, `UserAssist`, jump lists, `ConsoleHost_history`.
- `$MFT`, **SRUM**, **WMI** logs, **Defender** logs and the event log.

## Method

1. **Entry**: Chrome/Edge history → phishing URL and time. `Referer` and URL shape confirm credential theft.

2. **RDP**: logon events (4624 type 10) plus GUI artifacts (`UserAssist`, recent items) show what the intruder did in session.

3. **Privilege**: `whoami /priv` reveals a volume-management privilege (**SeManageVolumePrivilege**) that allows writing to protected paths.

4. **DLL**: a `PrintConfig.dll` (or similar) is downloaded with `certutil` — a LOLBIN — and placed on a `wmiprvse.exe` search path.

5. **Persistence**: search-order hijacking makes `wmiprvse.exe` load the DLL every time WMI is used (T1574.001). Confirm process and time in SRUM/Defender.

## What it teaches

- A "disk management" privilege can mean arbitrary writes under `C:\Windows`.
- `certutil` remains the favourite downloader: a signed, allowed LOLBIN.
- DLL search-order hijacking in a system process gives persistence without new services.
- Browser → RDP → MFT → SRUM correlation builds the full story.

## Pitfalls

- **The MFT is not a log**: entries get reused; for exact "when", cross-check SRUM and events.
- **Legit-looking DLL name**: the name hides nothing; the path and the loading process do.
- **Missing prefetch**: it may be disabled on Windows 10/11; do not conclude nothing ran.
