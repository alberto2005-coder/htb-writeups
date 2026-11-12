---
sherlock: Infiltrate
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, network, pcap, windows, initial-access, lateral-movement]
---

# Infiltrate — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no original evidence or literal answers.

## TL;DR

Investigation of an intrusion with network and host evidence. The PCAP identifies initial access, credentials and lateral movement; Windows logs confirm sessions and processes. Correlation reconstructs scope.

## Scenario

The organisation detects suspicious connections to an internal server. A PCAP and log collection are provided; identify the attacker, access method and affected hosts.

## Artifacts

- PCAP with HTTP/SMB/WinRM traffic.
- Security/System EVTX.
- Application and proxy logs.
- Session and process listings.

## Methodology

1. Review protocols and conversations in Wireshark/Zeek.
2. Extract credentials, user-agents and HTTP paths.
3. Identify SMB/WinRM access and source/destination hosts.
4. Cross-check IPs and accounts with EVTX.
5. Document the chain and compromised systems.

```bash
tshark -r capture.pcap -q -z conv,tcp
zeek -r capture.pcap
```

## Sample questions

- Which service was used for initial access?
- Which credentials were sent?
- Which host acted as a pivot?
- Which systems were accessed afterwards?
- What data was transferred?

## Tools

`Wireshark`, `tshark`, `Zeek`, `NetworkMiner`, `EvtxECmd`.

## Evidence and redaction

Screenshots of conversations and events are kept with IPs, users and credentials redacted. No literal answers are published.

## Lessons learned

- PCAP reveals credentials and paths logs may omit.
- SMB/WinRM are common lateral-movement channels.
- IP/account correlation validates the timeline.
- Encrypted traffic requires host logs.

## Detection

- Alert on SMB/WinRM from non-admin hosts.
- Monitor anomalous user-agents and paths.
- Correlate type 3/10 logons with network flows.
- Review outbound data transfers.

## References

- <https://app.hackthebox.com/sherlocks/Infiltrate>
- <https://attack.mitre.org/tactics/TA0008/>
- <https://www.wireshark.org/docs/>
