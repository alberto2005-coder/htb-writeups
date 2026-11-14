---
challenge: It Has Begun
type: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, windows, powershell, evtx, logs]
---

# It Has Begun — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

A set of Windows logs from an intrusion is provided. Analysing PowerShell, process events and the timeline reveals the command the attacker ran and leads to the flag.

## Prompt and surface

- Forensics, Very Easy, retired.
- A compressed archive with Windows artefacts is provided.
- The goal is to reconstruct the initial activity.

```bash
unzip evidence.zip -d evidence
find evidence -type f -maxdepth 3
```

## Reconnaissance

```bash
file evidence/*
sha256sum evidence/*
```

- EVTX files, transcripts or an event dump are present.
- Names and timestamps place the activity.
- Document custody before opening anything.

## Analysis

Load the EVTX with `EvtxECmd` or `Get-WinEvent`. Filter PowerShell (4103/4104), process creation (4688) and service events. The sequence shows the command, user and host.

```powershell
Get-WinEvent -Path .\Security.evtx -FilterXPath "*[System[EventID=4688]]"
```

## Exploitation

There is no remote exploitation: answer the challenge questions from the evidence. The flag appears after reconstructing the command or artefact name; do not publish it.

```bash
EvtxECmd.exe -f Security.evtx --csv out
```

## Evidence

- Correlated PowerShell and process events.
- User, host and time of the command.
- Timeline consistent with the scenario.

## Lessons

- EVTX preserves much more than errors.
- PowerShell and process creation complement each other.
- A timeline reduces noise.
- Custody starts before analysis.

## Mitigations and detection

- Enable Script Block Logging and process auditing.
- Centralise logs and protect their integrity.
- Alert on PowerShell with encoded commands.
- Review retention and log access.
- References: SANS Windows Forensics, EvtxECmd.

## References

- <https://www.hackthebox.com/challenges/It%20Has%20Begun>
- <https://github.com/EricZimmerman/EvtxECmd>
- <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows>
- <https://attack.mitre.org/techniques/T1059/001/>
