---
sherlock: OpTinselTrace-5
domain: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, chainsaw, ransomware, services]
---

# OpTinselTrace-5 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological note; no literal answers.

## Scenario

The final case in the saga. A collection of Windows event logs from a compromised environment is provided; reconstruct the malicious service installation, propagation and ransomware deployment. There are tens of thousands of Sigma matches, so filtering and ordering are key.

## Evidence

- `Logs/` with System, Security, Application and PowerShell EVTX.
- Sigma rules and Chainsaw.
- Service (7045), scheduled task and process events.
- Encryption and ransom-note indicators.

```bash
chainsaw hunt Logs/ -s sigma/ --mapping mappings/ --csv results.csv
```

## Investigation

### 1. Inventory and triage

Identify the host and time range. Run Chainsaw with Sigma rules and group by technique:

```bash
chainsaw hunt Logs/ -s sigma/ --mapping mappings/ --csv results.csv
cut -d, -f3 results.csv | sort | uniq -c | sort -nr | head
```

Prioritise 7045 (new service), 4697, 4688, 4104 (PowerShell) and 106/2004 (Defender).

### 2. Timeline

- Initial access and elevation.
- Service installation with a binary in `ProgramData` or `Temp`.
- Lateral movement (SMB, WinRM, PsExec).
- Ransomware execution and note creation.
- Log clearing or evasion attempts.

```bash
chainsaw search -t 'Event.System.EventID: =7045' Logs/
```

### 3. Key artefact

Event 7045 provides `ServiceName`, `ImagePath` and `ServiceType`. The binary path and installing user usually identify the stage. Events 4688/4104 reconstruct the chain up to encryption.

```text
7045 -> ImagePath -> process -> encryption/note
```

## Findings

- The attacker installed one or more services to run the ransomware.
- Propagation used credentials and remote administration tools.
- Logs order service installation, execution and encryption.
- IOCs are service names/paths, hashes, accounts and hosts.

## Lessons

- 7045 is the most direct event for malicious services.
- Chainsaw + Sigma reduces tens of thousands of events to a manageable list.
- Compare service time with the first ransom note.
- Missing PowerShell logs do not mean PowerShell was not used.

## References

- <https://mwalkowski.com/post/sherlock-optinseltrace-5>
- <https://github.com/WithSecureLabs/chainsaw>
- <https://attack.mitre.org/techniques/T1543/003/>
