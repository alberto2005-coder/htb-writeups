---
sherlock: Litter
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, pcap, dns-tunneling, dnscat2, exfiltration]
---

# Litter — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

A shared test host, outside the corporate network but with access to internal resources, has been compromised. A ZIP of evidence and a PCAP of the suspicious traffic are provided; the job is to work out which tool the attacker used, how the data left, and how many records went with it.

## Evidence

- A password-protected ZIP (password from the scenario).
- `suspicious_traffic.pcap`.
- A `README` with the scenario and the questions.

Good practice before touching anything:

```bash
sha256sum litter.zip suspicious_traffic.pcap   # record hashes
unzip -l litter.zip
capinfos suspicious_traffic.pcap
```

## Investigation

### 1. What the traffic is

`capinfos` gives duration, packet count and protocols. With the PCAP open in Wireshark, the filter that cuts the noise is volume plus rarity:

```text
dns.qry.name contains "microsofto365.com"
```

Hundreds of long, high-entropy `TXT`/`CNAME` queries to a domain imitating a legitimate service: DNS tunnelling, not real resolution.

### 2. Identifying the tool

The tunnel signature (labels, subdomain length, answer pattern) points at **dnscat2**. Decoding the stream confirms it:

```bash
python3 dnscat2-decoder/dnscat2_decoder.py suspicious_traffic.pcap microsofto365.com > dnscat_dump.txt
```

The dump holds the rebuilt session: commands, output and transferred files. That answers the client version (**dnscat2-v0.07-client**), the name the attacker gave the binary on the host, and what was exfiltrated. The tunnel server is `192.168.157.145`.

### 3. Sizing the damage

The dump shows the command that read the PII CSV and the total record count. Watch the count: the index starts at zero, so with the last record at 720 the total is **721**.

## Findings

- Channel: **DNS tunnelling** with dnscat2 over a legitimate-looking domain.
- Target: customer PII from a database on the test host.
- The host was not monitored like production, which is exactly what made it attractive.

## Lessons

- DNS is almost never filtered at egress: it is the most convenient exfiltration channel left.
- Detection leans on per-domain volume and entropy, not malware signatures.
- Mitigation: resolve only through internal resolvers, restrict `TXT` and `NULL`, and alert on queries per minute and label length.
