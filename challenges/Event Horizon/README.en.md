---
challenge: Event Horizon
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, windows, evtx, powershell, event-logs]
---

# Event Horizon — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real flag.

## TL;DR

A collection of EVTX logs from a compromised Windows host is provided. Classic PowerShell logs were cleared, but operational and scripting events remain and reveal the command and flag. Parse every EVTX, not just `Microsoft-Windows-PowerShell`.

## Brief and surface

- Forensics, Easy, retired.
- `Logs/` with hundreds of EVTX files.
- Auxiliary `TraceFormat` folder.
- The brief says PowerShell logs were cleared.

```bash
find Logs -name '*.evtx' | wc -l
```

## Recon

List channels and look for PowerShell, WMI and scripting:

```bash
find Logs -iname '*PowerShell*' -o -iname '*WMI*'
```

```text
Microsoft-Windows-PowerShell%4Operational.evtx
Microsoft-Windows-PowerShell%4Admin.evtx
Microsoft-Windows-WMI-Activity%4Operational.evtx
```

## Source analysis

There is no binary: the artefact is EVTX. Convert it to XML/JSON with `evtx_dump.py` or `EvtxECmd`:

```bash
python3 evtx_dump.py 'Logs/Microsoft-Windows-PowerShell%4Operational.evtx' > ps.xml
grep -iE 'ScriptBlock|4104|CommandLine|flag' ps.xml | head
```

Chainsaw with Sigma rules can also locate suspicious execution.

## The bug

Clearing PowerShell logs does not remove already-written operational events or copies in other channels. The attacker relies on partial cleanup; the analyst must review every EVTX and scripting event (4104).

## Local reproduction

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install python-evtx
python3 evtx_dump.py 'Logs/Microsoft-Windows-PowerShell%4Operational.evtx' > ps.xml
```

Find the script block, decode base64 if present and extract the flag. Verify it on the platform.

## Exploitation

There is no server. Exploitation is forensic: rebuild the command from events and decode the payload. Redact the flag.

## Evidence

- Number of EVTX files and relevant channels.
- 4104 event with the script redacted.
- Redacted flag.

## Lessons learned

- Operational logs survive clearing of classic logs.
- 4104 records script blocks and is key for PowerShell.
- Review WMI and Task Scheduler, not just PowerShell.
- Log clearing is selective and leaves traces.

## Mitigations and detection

- Centralise logs in a SIEM before an attacker can delete them.
- Enable Script Block Logging and transcription.
- Alert on 1102 (log clearing) and sudden gaps.
- Restrict permissions to clear logs.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/event-horizon/>
- <https://github.com/williballenthin/python-evtx>
- <https://attack.mitre.org/techniques/T1070/001/>
