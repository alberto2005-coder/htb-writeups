---
sherlock: SalineBreeze-2
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, breach, logs, pcap, lateral-movement]
---

# SalineBreeze-2 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

Breach investigation across multiple sources: access logs, PCAP and authentication events. Initial access, escalation and lateral movement are reconstructed.

## Scenario

An organisation detects anomalous activity on several servers. Logs and network captures are provided to determine scope and compromised accounts.

## Artefacts

- Access logs and auth logs.
- Internal traffic PCAP.
- EVTX/Syslog and IDS alerts.
- Account and host inventory.

## Methodology

1. Fix the timeline and identify traffic spikes.
2. Look for brute force, web shells and tunnels.
3. Correlate internal IPs with accounts and processes.
4. Review SMB/RDP/WinRM for lateral movement.
5. Document IOCs and impact.

```bash
zeek -r capture.pcap
cat access.log | awk '{print $1}' | sort | uniq -c | sort -nr
```

## Sample questions

- What was the initial access?
- Which accounts were compromised?
- Which hosts were used to pivot?
- Which data left?
- Which IOC detects the campaign?

## Tools

`Zeek`, `Wireshark`, `grep/awk`, `EvtxECmd`, `Timeline Explorer`.

## Evidence and redaction

Flow screenshots and hashes are kept with IPs, users and domains redacted.

## Lessons learned

- Log and PCAP correlation narrows scope.
- Tunnels leave recognizable flow patterns.
- Lateral movement uses valid credentials.
- An isolated IOC does not explain the chain.

## Detection

- Alert on brute force followed by success.
- Monitor web shells and server processes.
- Detect unusual internal SMB/RDP.
- Correlate DNS and outbound connections.

## References

- <https://app.hackthebox.com/sherlocks/SalineBreeze-2>
- <https://attack.mitre.org/techniques/T1021/>
- <https://docs.zeek.org/>
