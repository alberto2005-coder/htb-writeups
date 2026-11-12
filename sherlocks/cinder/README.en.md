---
sherlock: Cinder
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, registry, persistence, mft]
---

# Cinder — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no original evidence or literal answers.

## TL;DR

Investigation of a Windows host showing persistence and unauthorised execution. EVTX, registry hives, prefetch and MFT are combined to identify the malicious binary, the startup mechanism and the account used.

## Scenario

A workstation shows suspicious activity after an incident. The response team collects triage artifacts and asks what ran, how it persisted and which accounts were affected.

## Artifacts

- Security, System and PowerShell EVTX.
- `NTUSER.DAT`, `SOFTWARE` and `SYSTEM`.
- Prefetch and `Amcache`.
- `$MFT` and temporary files.

## Methodology

1. Review `Run`, `RunOnce`, services and scheduled tasks.
2. Identify the binary and path; confirm creation in `$MFT`.
3. Correlate with prefetch/Amcache to confirm execution.
4. Review events 4688, 7045 and 4104.
5. Document the account, parent process and persistence.

```bash
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run
EvtxECmd.exe -d C:\Evidence\evtx --csv C:\Evidence\out
PECmd.exe -d C:\Evidence\prefetch --csv C:\Evidence\pf
```

## Sample questions

- Which binary ran anomalously?
- Which registry key or service starts it?
- Which account executed it?
- When was the file created?
- Were artifacts deleted afterwards?

## Tools

`Registry Explorer`, `EvtxECmd`, `PECmd`, `MFTECmd`, `Timeline Explorer`.

## Evidence and redaction

Screenshots of keys, events and the timeline are kept with users and paths redacted. No literal answers are published.

## Lessons learned

- `Run` keys and services are common persistence points.
- Prefetch and Amcache confirm execution even if the binary is gone.
- The parent process separates legitimate installers from abuse.
- A missing file does not mean no execution.

## Detection

- Alert on new services and `Run` keys outside installers.
- Monitor binaries in `AppData`/`ProgramData`.
- Correlate 7045 with file creation.
- Review scheduled tasks created outside the change window.

## References

- <https://app.hackthebox.com/sherlocks/Cinder>
- <https://attack.mitre.org/techniques/T1547/001/>
- <https://attack.mitre.org/techniques/T1543/003/>
