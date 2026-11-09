---
sherlock: Logjammer
domain: Log Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, evtx, windows-events, firewall, scheduled-task, powershell, sharphound]
---

# Logjammer — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

A DFIR technical assessment: **five event channels** exported from a single Windows host (`DESKTOP-887GK2L`), used by the `cyberjunkie` account. Reconstruct all post-compromise activity: first logon, firewall rules, audit changes, scheduled tasks, PowerShell executed and destroyed evidence.

## Evidence

```text
System.evtx
Security.evtx
Powershell-Operational.evtx
Windows Firewall-Firewall.evtx
Windows Defender-Operational.evtx
```

## Investigation

### 1. Parse and baseline

```bash
EvtxECmd.exe -d ./logs -o out/ --csv out/
```

Load the full CSV in Timeline Explorer, filter by `EventID` and sort by time. Fix the timezone first: events are UTC and many questions ask for local time.

### 2. First access and session

- **4624** (successful logon) with `LogonType` 2/10 and user `cyberjunkie`: gives the time of first access.
- **4634/4647** close the session; they separate blocks of activity.

### 3. Persistence and configuration

- **4698**: scheduled task created. The embedded XML holds the script path and schedule. This is what survives a reboot.
- **4719**: audit policy change (someone preparing to erase or dodge logs).
- **2004** in the firewall channel: rule created with numeric fields (`Direction 2` = outbound, `Protocol 6` = TCP, `RemotePort 4444`). Translate the codes before answering; an outbound rule to 4444 is a C2.

### 4. Tooling and execution

- **1116/1117** in Defender: detection and action on an AD reconnaissance tool (SharpHound). Even quarantined, the detection reveals intent.
- **4104** in PowerShell Operational: ScriptBlock with the actual command. This is the source that says *what* ran, not merely that PowerShell started.

### 5. Evidence destruction

- **104** in the firewall channel: the log was cleared. The deletion itself generates the event flagging the tampered channel. Cross-check **1102** (Security) when present.

## Findings

- Hands-on-keyboard activity with scheduled-task persistence and an outbound rule to 4444.
- AD reconnaissance with SharpHound, caught by Defender.
- Log-clearing attempt that leaves a trace in the firewall channel.

## Lessons

- Five crossed channels tell a story; one alone does not.
- The firewall's numeric `EventID` fields (direction, action, protocol) must be translated, not guessed.
- Mitigation: forward logs to a central server (WEF/SIEM) so local deletion cannot destroy evidence, and alert on `4719` and `104`.
