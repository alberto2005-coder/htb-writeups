---
sherlock: Salsa Dance
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, mft, powershell, timeline]
---

# Salsa Dance — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; original evidence was not downloaded.

## TL;DR

DFIR case on a compromised Windows host. The investigation combines EVTX, MFT, PowerShell history and execution artifacts to reconstruct initial access, persistence and exfiltration. The goal is a defensible timeline that separates legitimate activity from the intruder's.

## Scenario

An organisation detects anomalous activity on a workstation. A Windows artifact collection is provided; identify the entry vector, affected accounts and stolen data.

## Artifacts

- Security, System, PowerShell and Defender EVTX.
- `$MFT` and USN journals.
- PowerShell history and prefetch.
- Browser and execution artifacts.
- No memory or full disk.

## Methodology

1. Inventory artifacts and hash them.
2. Convert EVTX to CSV/JSON and filter by time window.
3. Review 4624/4625, 4688, 4104 and 7045 for logons, processes, scripts and services.
4. Cross-check `$MFT` with prefetch and USN to confirm creation and execution.
5. Review downloads, temp files and outbound connections.
6. Build the timeline and document gaps.

```bash
EvtxECmd.exe -d C:\Evidence\evtx --csv C:\Evidence\out
MFTECmd.exe -f C:\Evidence\$MFT --csv C:\Evidence\mft
```

## Sample questions

- What was the first access and with which account?
- Which PowerShell script ran and why?
- What persistence mechanism was created?
- Which files were compressed or exfiltrated?
- Which activity is legitimate and which is the attacker's?

## Tools

`EvtxECmd`, `MFTECmd`, `Timeline Explorer`, `Chainsaw`, `jq`, `grep`.

## Evidence and redaction

Screenshots of events and the timeline are kept with users, IPs and paths redacted. No literal answers or flags are published.

## Lessons learned

- EVTX/MFT/prefetch correlation reduces false positives.
- PowerShell history and 4104 reconstruct scripts.
- Service 7045 is a persistence indicator.
- A timeline with documented gaps beats a raw IOC list.

## Detection

- Alert on 7045 with binaries outside `System32`.
- Correlate type 3/10 logons with unusual hours.
- Monitor compression and outbound transfers.
- Review PowerShell with `-enc` and HTTP downloads.

## References

- <https://app.hackthebox.com/sherlocks/SalsaDance>
- <https://attack.mitre.org/tactics/TA0003/>
- <https://learn.microsoft.com/en-us/powershell/scripting/windows-powershell/wmf/overview>
