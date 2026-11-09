---
sherlock: Compromised
domain: DFIR / Network
difficulty: Easy
platform: Hack The Box
evidence: Packet capture from a corporate network
tools: [Wireshark, tshark, NetworkMiner]
---

# Compromised — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

There are signs of malicious traffic and at least one compromised host that held sensitive data. A PCAP is provided to identify initial access, the affected machine and what was taken.

## Evidence

- A single `capture.pcap`.

## Method

1. **Overview**: `Statistics → Conversations` shows who talks to whom and how much.

```bash
tshark -r capture.pcap -q -z conv,ip
tshark -r capture.pcap -q -z io,phs
```

2. **Initial access**: look for HTTP requests with suspicious parameters or cleartext credentials, and exposed administration protocols (SMB, RDP, WinRM, FTP).

```bash
tshark -r capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

3. **Compromised host**: the one receiving the exploit and then producing downloads or new outbound connections. Map the IP to NetBIOS/DNS names.

4. **Exfiltration**: files under `Export Objects → HTTP/SMB` and anomalous volumes in a specific stream (`Follow TCP Stream`).

5. **Timeline**: order key events by `frame.time` (login, webshell upload, data download).

## What it teaches

- In a PCAP, initial access usually hides in cleartext HTTP or an unencrypted administration protocol.
- The compromise's fingerprint is not only the entry: the **outbound** data confirms impact.
- Exporting objects reveals what was downloaded or stolen without hand-rebuilding the protocol.

## Pitfalls

- **Partial capture**: it may start mid-intrusion; do not assume the first packet is the beginning.
- **TLS**: when the channel is encrypted, rely on metadata (SNI, certificates, volumes, times).
- **Scan filler**: separate discovery noise from exploitation traffic.
