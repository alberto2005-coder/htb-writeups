---
sherlock: SmartyPants
category: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, rdp, smartscreen, timeline]
---

# SmartyPants — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; original evidence was not downloaded.

## TL;DR

A Windows file server was accessed over RDP, wiping and exfiltration utilities were installed, and logs were later cleared. EVTX records reconstruct initial access (1149), tool execution, data copying and log clearing (1102). SmartScreen adds context on downloads and executables.

## Scenario

The CTO stores critical files on a Windows server separate from the domain. An intruder accesses it over RDP, installs utilities, steals data and deletes it. The organisation receives an extortion demand and requests forensic triage.

## Artifacts

- EVTX collection from the compromised host.
- SmartScreen logs.
- Execution metadata and timeline.
- No full disk image.

## Methodology

1. Inventory EVTX channels and convert them to JSON/CSV with `EvtxECmd` or `evtx_dump`.
2. Find Terminal Services event 1149 for the first successful RDP logon.
3. Review `Microsoft-Windows-SmartScreen` and execution events to identify downloaded or installed binaries.
4. Locate wiping utilities (`Everything`, `File Shredder`) and confirm log-clearing event 1102.
5. Build a timeline in `Timeline Explorer` and answer the Sherlock questions.

```bash
EvtxECmd.exe -d C:\Evidence\evtx --csv C:\Evidence\out
```

## Sample questions

- When did the first RDP access occur?
- Which utility was used to locate files?
- Which tool wiped the data?
- At what time were the logs cleared?
- Which SmartScreen executable is linked to the intrusion?

## Tools

`EvtxECmd`, `Timeline Explorer`, `jq`, `grep`, `Chainsaw`.

## Evidence and redaction

Screenshots of events and the timeline are kept with usernames, IPs and sensitive paths redacted. No literal answers or flag are published.

## Lessons learned

- Event 1149 identifies successful RDP logons.
- SmartScreen helps reconstruct downloads and executions.
- Event 1102 confirms log clearing but does not erase copied EVTX.
- Missing classic logs do not prevent reconstruction.

## Detection

- Alert on 1149 from unusual IPs.
- Correlate 1102 with wiping and exfiltration activity.
- Monitor installation of `Everything` and shredding tools.
- Centralise logs before an attacker can clear them.

## References

- <https://app.hackthebox.com/sherlocks/SmartyPants>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-1102>
- <https://attack.mitre.org/techniques/T1070/001/>
