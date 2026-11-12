---
sherlock: Alchemy
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, powershell, credential-access, scheduled-task, evtx]
---

# Alchemy — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

A Windows host shows obfuscated PowerShell execution and credential access. The chain is reconstructed with 4104, 4688, scheduled tasks and memory/registry artefacts.

## Scenario

A scheduled task launching PowerShell with an encoded payload is detected. The response team provides logs and artefacts to identify its purpose and scope.

## Artefacts

- PowerShell Operational (4103/4104).
- Security (4688, 4672, 4624).
- Task Scheduler and registry.
- `$MFT`, prefetch and memory.

## Methodology

1. Decode the PowerShell payload and identify functions and URLs.
2. Review the parent process and the account that created the task.
3. Look for LSASS/SAM access and dumps.
4. Correlate with file creation and network connections.
5. Document persistence and impact.

```bash
EvtxECmd.exe -f 'Microsoft-Windows-PowerShell%4Operational.evtx' --csv C:\\Evidence\\ps
Get-ScheduledTask | Export-Csv tasks.csv
```

## Sample questions

- Which task schedules execution?
- What does the obfuscated payload do?
- Which credentials or databases does it access?
- Which user created it?
- Was data exfiltrated?

## Tools

`EvtxECmd`, `PowerShell Log Parser`, `Timeline Explorer`, `Volatility`, `PECmd`.

## Evidence and redaction

Screenshots of the decoded payload and timeline are kept with users, paths and domains redacted.

## Lessons learned

- 4104 is key for obfuscated PowerShell.
- Scheduled tasks provide persistence and execution.
- LSASS access leaves events and handles.
- Decode in an isolated environment.

## Detection

- Alert on PowerShell with `-enc` and new tasks.
- Monitor LSASS access by unsigned processes.
- Correlate 4104 with 4688 and network.
- Restrict task creation to administrators.

## References

- <https://app.hackthebox.com/sherlocks/Alchemy>
- <https://attack.mitre.org/techniques/T1059/001/>
- <https://attack.mitre.org/techniques/T1053/005/>
