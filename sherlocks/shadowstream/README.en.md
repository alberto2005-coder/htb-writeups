---
sherlock: ShadowStream
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, loader, multi-stage, c2, persistence]
---

# ShadowStream — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original sample or real IOCs.

## TL;DR

Multi-stage loader that downloads a payload from a C2, runs it in memory and establishes persistence. Sample, network and host analysis reconstruct each stage.

## Scenario

A host shows a low-reputation process and periodic traffic. The initial sample and artefacts are provided to identify the final payload and persistence.

## Artefacts

- Loader PE and resources.
- PCAP/TLS and proxy logs.
- Memory and processes.
- `Run`, tasks and services.

## Methodology

1. Analyse the loader with DIE/CAPA and locate URLs.
2. Review configuration and user-agent.
3. Capture the second stage on the wire or in memory.
4. Identify the execution technique (injection, `rundll32`, `regsvr32`).
5. Document persistence and IOCs.

```bash
capa -vv loader.exe
vol.py -f mem.raw pstree
vol.py -f mem.raw netscan
```

## Sample questions

- How many stages are there?
- Which URL downloads the second stage?
- Where does the payload run?
- How does it persist?
- Which C2 does the final payload use?

## Tools

`CAPA`, `Detect It Easy`, `Volatility`, `Wireshark`, `Procmon`.

## Evidence and redaction

Hashes, captures and memory regions are kept with IPs/domains redacted.

## Lessons learned

- Loaders separate download from execution.
- Memory retains the payload if the file is deleted.
- Persistence may be installed by the second stage.
- Periodic traffic helps find the C2.

## Detection

- Alert on processes that download and execute in memory.
- Monitor `rundll32`/`regsvr32` with URLs.
- Correlate periodic connections.
- Apply YARA in memory and on disk.

## References

- <https://app.hackthebox.com/sherlocks/ShadowStream>
- <https://attack.mitre.org/techniques/T1105/>
- <https://attack.mitre.org/techniques/T1055/>
