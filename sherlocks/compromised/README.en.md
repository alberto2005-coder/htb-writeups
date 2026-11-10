---
sherlock: Compromised
domain: DFIR / Network
difficulty: Easy
platform: Hack The Box
evidence: Packet capture from a corporate network
tools: [Wireshark, tshark, NetworkMiner, VirusTotal]
state: Retired
tags: [dfir, network-forensics, pcap, malware-triage, dns-tunneling]
---

# Compromised — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

The SOC spots suspicious traffic: a host on the corporate network is compromised and data that should never have left is gone. One PCAP is provided; rebuild initial access, classify the malware and say what was exfiltrated.

## Evidence

- `capture.pcap`.

## Method

1. **Overview**: who talks to whom, and how much.

```bash
tshark -r capture.pcap -q -z conv,ip
```

2. **Initial download**: the victim requests, over plain HTTP, a file named like an image (`6ctf5JL.gif`) from `162.252.172.54`, but the payload is a **PE DLL**.

```bash
tshark -r capture.pcap -Y 'http.request' -T fields -e ip.dst -e http.host -e http.request.uri
```

`Export Objects` truncates the stream: reassemble the TCP flow, confirm with `file` that it is a PE and **then** hash it, or the SHA-256 will not match any database.

3. **Classification**: that SHA-256 on VirusTotal identifies it as **Pikabot** (a loader); the same record gives the family label and the first-seen date the attribution questions ask for.

4. **C2**: after execution the host speaks **HTTPS with self-signed certificates** to external hosts on non-standard ports (2078, 2222 and 3299).

```bash
tshark -r capture.pcap -Y 'ssl.handshake.type==11' -T fields -e ip.dst -e tcp.port -e x509sat.printableString
```

5. **Exfiltration**: the final channel is neither HTTP nor TLS but **DNS**: long names and an anomalous volume towards an attacker domain, a tunnel pattern.

```bash
tshark -r capture.pcap -Y dns -T fields -e dns.qry.name | sort | uniq -c | sort -rn | head
```

## Findings

One PCAP holds the whole chain: a Pikabot DLL pulled over HTTP from `162.252.172.54`, self-signed TLS beacons on high ports, and data leaving over a DNS tunnel. The family comes from VirusTotal, not from decrypting traffic.

## Lessons

- The download hides as an image: the name says nothing, the `MZ` signature does.
- Wireshark's object export truncates large flows; reassemble before hashing.
- Three different protocols (HTTP, TLS, DNS) and only network visibility ties them together.

## What it teaches

- A modern C2 switches channel per stage: download, beacons, egress.
- Self-signed certificates on high ports are a cheap, strong signal.
- DNS tunnelling shows up in name length and volume, with nothing decrypted.

## Pitfalls

- **TLS**: without keys the content stays closed; analysis runs on metadata (SNI, certificate, ports, volumes).
- **Noise**: separate discovery traffic from exploitation.
- **Hashes**: hashing the exported object instead of the reassembled flow yields a value no database knows.
