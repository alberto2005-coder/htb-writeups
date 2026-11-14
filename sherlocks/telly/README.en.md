---
sherlock: Telly
category: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, telnet, cve-2026-24061, exfiltration]
---

# Telly — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal answers or real data.

## Scenario

An MSSP analyses traffic from a rarely used backup server. A DLP solution flags possible exfiltration. A one-hour PCAP is provided; reconstruct access and data loss.

## Evidence

- `monitoringservice_export_202610AM-11AM.pcapng` (about 23,000 packets).
- Telnet, HTTP and external connections.
- No disk or memory.

```bash
capinfos monitoringservice_export_202610AM-11AM.pcapng
tshark -r capture.pcapng -q -z io,phs
```

## Investigation

### 1. Inventory and triage

Review protocols and conversations. Cleartext Telnet exposes credentials and commands; a session from an external IP is the first indicator.

```bash
tshark -r capture.pcapng -Y 'telnet' -T fields -e ip.src -e ip.dst -e telnet.data
```

### 2. Timeline

Follow the main TCP stream:
- Telnet service connection.
- Enumeration commands.
- Creation of a service account.
- Download of a persistence script.
- Reading and compressing a database.

The associated vulnerability is CVE-2026-24061 in `telnetd` (GNU InetUtils), allowing root authentication.

### 3. Key artefact

The stream contains account creation and the `linper.sh` download. A card database is then exfiltrated; the attacker deletes it at the end.

## Conclusions

- Initial access was exploitable Telnet, not brute force.
- The attacker established persistence and exfiltrated customer data.
- Cleartext traffic allowed full reconstruction.
- Rotate credentials and review the server.

## Lessons

- Telnet must not be exposed.
- Unencrypted management traffic helps both attackers and DFIR.
- Exfiltration can happen in minutes.

## References

- <https://www.hackthebox.com/sherlocks/Telly>
- <https://nvd.nist.gov/vuln/detail/CVE-2026-24061>
- <https://attack.mitre.org/techniques/T1048/>
