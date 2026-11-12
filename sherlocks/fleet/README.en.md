---
sherlock: Fleet
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, fleet, evtx, lateral-movement, timeline]
---

# Fleet — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no original evidence or literal answers.

## TL;DR

Investigation of a Windows endpoint fleet. Artifacts from multiple hosts are compared to identify patient zero, lateral movement and affected systems. The key is a normalised cross-host timeline instead of isolated analysis.

## Scenario

Several organisational endpoints raise related alerts. A fleet triage collection is provided; determine scope, origin and propagation.

## Artifacts

- Security/System EVTX per host.
- Prefetch, Amcache and `$MFT`.
- Process and connection listings.
- Local users and scheduled tasks.
- Fleet inventory.

## Methodology

1. Inventory hosts, names and collection times.
2. Normalise time zones and build a common timeline.
3. Look for type 3/10 logons and SMB/WinRM access between hosts.
4. Compare processes and binaries with the legitimate inventory.
5. Identify patient zero and propagation order.
6. Document compromised accounts and unaffected systems.

```bash
EvtxECmd.exe -d C:\Fleet\Host01\evtx --csv C:\Fleet\out\host01
PECmd.exe -d C:\Fleet\Host01\prefetch --csv C:\Fleet\out\pf01
```

## Sample questions

- Which host was compromised first?
- Which accounts were used for lateral movement?
- Which binary or service propagated?
- Which hosts were affected?
- Which activity predates the incident?

## Tools

`EvtxECmd`, `PECmd`, `MFTECmd`, `Timeline Explorer`, `jq`.

## Evidence and redaction

Screenshots of the multi-host timeline are kept with names, IPs and accounts redacted. No literal answers are published.

## Lessons learned

- Analyse the fleet as a whole, not host by host.
- Normalise time zones before comparison.
- WinRM/SMB leave traces on source and destination.
- A legitimate inventory reduces false positives.

## Detection

- Correlate type 3/10 logons between workstations.
- Alert on service creation across multiple hosts.
- Monitor binary propagation over SMB.
- Maintain an inventory and process baseline.

## References

- <https://app.hackthebox.com/sherlocks/Fleet>
- <https://attack.mitre.org/tactics/TA0008/>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624>
