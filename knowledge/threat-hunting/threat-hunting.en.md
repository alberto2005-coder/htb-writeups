---
title: "Threat hunting: hypotheses, pivots and evidence"
tags: [threat-hunting, dfir, evtx, sysmon, pcap, mitre]
---

# Threat hunting: hypotheses, pivots and evidence

**English** | [🇪🇸 Español](threat-hunting.md)

## 1. When to look here

A low-confidence alert, a freshly deployed SOC, or an incident with an incomplete capture. Hunting does not start with a tool but with a verifiable **hypothesis**: "a service created under a user path means execution as SYSTEM", "an Office process spawning `certutil` means a download". Without a hypothesis you only have IOC search, and IOCs expire.

## 2. The cycle

1. **Hypothesis**: which technique you suspect and which artifact would prove it.
2. **Sources**: what data you have and what is missing (EVTX, Sysmon, Prefetch, Amcache, MFT, PCAP, EDR).
3. **Query**: one concrete search, with a time window and scope.
4. **Triage**: separate the anomalous from the normal using a baseline.
5. **Pivot**: from one finding to another artifact that confirms or rules it out.
6. **Conclusion**: technique, evidence, impact and derived detections.

## 3. Sources that resolve the most

| Artifact | What it answers | Tool |
|---|---|---|
| `System.evtx` (7045) | services created and their binary | EvtxECmd, Event Viewer |
| `Security.evtx` (4624/4625/4688) | logons, logon type, processes | EvtxECmd, Hayabusa |
| Prefetch | execution and first/last run | PECmd |
| Amcache | executable SHA1 and paths | AmcacheParser |
| `Windows.edb` | indexed document content | SIDR |
| `CryptnetUrlCache` | URLs and content fetched by `certutil` | direct review |
| `PSReadLine` | commands typed in PowerShell | `ConsoleHost_history.txt` |
| `NTUser.dat` → UserAssist | programs used and focus time | Registry Explorer |
| `UsrClass.dat` → shellbags | folders visited | ShellBags Explorer |
| PCAP | C2, exfiltration, cleartext credentials | Wireshark, `tshark` |

## 4. Useful commands

```bash
EvtxECmd.exe -f System.evtx --csv . --csvf system
PECmd.exe -d Prefetch --csv . --csvf prefetch
AmcacheParser.exe -f Amcache.hve --csv . --csvf amcache
tshark -r capture.pcap -Y "ftp || ftp-data" -T fields -e ip.src -e ip.dst -e ftp.request.command
```

To correlate, normalise everything to UTC and sort by time. A `4624` type 3 followed by `whoami` and `certutil` tells a story; each event alone does not.

## 5. Typical pivots

- Randomly named service → hash in Amcache → VT and binary prefetch.
- `certutil` in Prefetch → `CryptnetUrlCache\MetaData` (URL) and `\Content` (file).
- Browser → download history → exfiltration and dumping tools.
- `PSReadLine` → renamed script → cmdlets that reveal the family.
- Shellbags → sensitive folder → ZIP → PCAP → FTP transfer.
- Process dump → product CVE → credentials → database.

## 6. Mapping to ATT&CK without inventing

Map what is **proven**, not assumed. A 7045 with a binary under `Users\` is T1569.002 (Service Execution); a `certutil -urlcache` is T1105 (Ingress Tool Transfer); a `4624` type 10 is T1021.001 (RDP). If evidence is insufficient, write "unconfirmed" and name the source that would settle it.

## 7. Documenting

- Timeline with time and timezone.
- Table finding → artifact → path → interpretation.
- IOCs separate from TTPs.
- Proposed detections: Sigma rule, KQL/Splunk query, YARA signature.
- Gaps: what could not be seen and why (partial capture, retention, sensor).

## 8. Typical errors

- **Starting from IOCs**: without a hypothesis, analysis dies at the first list.
- **Timezone**: mixing local and UTC shifts the chain and breaks correlation.
- **A single source**: a 7045 without its 4624 does not prove who logged in.
- **Confusing absence with non-existence**: no event does not mean no activity; telemetry may be missing.
- **Conclusions without a path**: without path and time the conclusion is not reproducible.

## 9. Detection and improvement

- Turn every finding into a rule and test it against the case itself.
- Measure coverage per technique (ATT&CK) and per source; find the gap before the attacker does.
- Retention and sizing: an incomplete capture limits the investigation; the endpoint must cover what the network cannot see.

MITRE: T1569.002, T1105, T1021.001, T1003.001. References: SANS FOR500, Eric Zimmerman's documentation and ATT&CK.
