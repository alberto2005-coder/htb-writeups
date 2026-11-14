---
sherlock: Smoke & Mirrors
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, evtx, powershell, sysmon, amsi, lsass]
---

# Smoke & Mirrors — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal answers or real data.

## Scenario

Operation Blackout 2025. A Windows host shows obfuscated PowerShell and defence changes. EVTX logs are provided; reconstruct execution, persistence and evasion.

## Evidence

- `Security.evtx`, `PowerShell Operational.evtx`, `Sysmon.evtx` and `System.evtx`.
- No memory or full disk.

```bash
EvtxECmd.exe -d . --csv out
chainsaw hunt . -s sigma/
```

## Investigation

### 1. Inventory and triage

Load the channels into Timeline Explorer and sort by time. Events 4104 (Script Block) and Sysmon 1 (process creation) provide the first timeline.

- PowerShell 4104 with encoded blocks or `IEX`.
- Sysmon 1 with `powershell.exe` and unusual arguments.
- Sysmon 13 for registry changes.

### 2. Timeline

Normalise the timezone and correlate:
- Process start and user.
- Script download or decoding.
- Service/task or `Run` key creation.
- Attempts to disable AMSI, Defender or LSA protection.

```bash
Get-WinEvent -Path 'PowerShell Operational.evtx' -FilterXPath "*[System[EventID=4104]]"
```

### 3. Key artefact

The 4104 block reconstructs the script. Decode base64, resolve variables and identify calls to `AmsiScanBuffer`, `VirtualProtect` or `lsass`. The registry key or service confirms persistence.

## Conclusions

- The attacker ran obfuscated PowerShell and tampered with defences.
- Persistence remained in the registry/service, depending on the artefact.
- IOCs include paths, process names and modified keys.
- The evidence supports detections for 4104 and Sysmon.

## Lessons

- 4104 is essential when memory is unavailable.
- AMSI evasion leaves traces in the script and calls.
- Without disk, persistence is confirmed through registry and services.

## References

- <https://www.hackthebox.com/sherlocks/Smoke%20%26%20Mirrors>
- <https://attack.mitre.org/techniques/T1059/001/>
- <https://attack.mitre.org/techniques/T1562/001/>
