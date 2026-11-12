---
sherlock: LATUS
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, timeline, evtx, mft, registry]
---

# LATUS — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

Multi-artefact investigation of a Windows host. EVTX, MFT, registry and execution artefacts reconstruct access, persistence and lateral movement.

## Scenario

A server shows compromise indicators across several artefacts. The response team asks for a single timeline and attribution of each action.

## Artefacts

- `Security.evtx`, `System.evtx`, PowerShell.
- `$MFT`, `$UsnJrnl`, prefetch and Amcache.
- `SYSTEM`, `SOFTWARE`, `NTUSER.DAT` hives.
- Application and network logs.

## Methodology

1. Inventory artefacts and fix time zones.
2. Build a timeline from EVTX/MFT.
3. Identify anomalous processes, services and tasks.
4. Cross-check accounts and network connections.
5. Separate legitimate activity from the attacker's.

```bash
EvtxECmd.exe -d C:\\Evidence\\evtx --csv C:\\Evidence\\out
MFTECmd.exe -f C:\\Evidence\\MFT --csv C:\\Evidence\\mft
TimelineExplorer.exe
```

## Sample questions

- What was the first access indicator?
- Which account was used?
- Which persistence was created?
- Which hosts were contacted?
- Which data was accessed?

## Tools

`EvtxECmd`, `MFTECmd`, `Registry Explorer`, `Timeline Explorer`, `Chainsaw`.

## Evidence and redaction

Timeline screenshots and hashes are kept with users, IPs and paths redacted.

## Lessons learned

- One source is not enough for attribution.
- A wrong time zone breaks the sequence.
- Execution artefacts confirm what logs suggest.
- Multi-host correlation reveals lateral movement.

## Detection

- Correlate 4624/4688/7045 in short windows.
- Alert on new services and tasks.
- Review admin-share access.
- Keep sufficient EVTX retention.

## References

- <https://app.hackthebox.com/sherlocks/LATUS>
- <https://attack.mitre.org/techniques/T1053/>
- <https://attack.mitre.org/techniques/T1021/>
