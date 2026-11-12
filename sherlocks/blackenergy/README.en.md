---
sherlock: BlackEnergy
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, blackenergy, dropper, c2, static-analysis, dynamic-analysis]
---

# BlackEnergy — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original sample or real IOCs.

## TL;DR

Analysis of a BlackEnergy-related sample. The dropper, persistence, C2 channel and remote execution capabilities are identified through static and controlled dynamic analysis.

## Scenario

A binary sample and host artefacts with periodic communications are provided. The goal is to classify the family, document execution flow and extract IOCs without running the sample in production.

## Artefacts

- PE binary and possible embedded resources.
- Communication PCAP.
- EVTX and persistence keys.
- Strings, imports and configuration.

## Methodology

1. Compute hashes and identify compiler/packer with `pefile` and Detect It Easy.
2. Review imports, sections and strings for URLs, keys and paths.
3. Run in an isolated VM with `procmon`, `procexp` and network capture.
4. Document parent process, created files, `Run` keys and traffic.
5. Extract IOCs and detection rules.

```bash
pefile sample.exe
strings -n 8 sample.exe | less
procmon /quiet
```

## Sample questions

- Which family or variant is it?
- Which persistence mechanism does it use?
- What is the C2 domain/IP?
- Which evasion techniques does it apply?
- Which processes does it launch and with what arguments?

## Tools

`Detect It Easy`, `pefile`, `Procmon`, `Wireshark`, `CAPA`, `YARA`.

## Evidence and redaction

Hashes, paths and traffic captures are kept with domains, IPs and keys redacted. The sample is not distributed.

## Lessons learned

- Static analysis narrows behaviour before execution.
- Persistence and C2 often live in resources/configuration.
- Periodic traffic helps identify the channel.
- IOCs must be validated against the incident context.

## Detection

- Look for service/`Run` key creation from non-installer processes.
- Block known C2 domains/IPs.
- Alert on periodic connections to new destinations.
- Apply YARA to binaries and memory.

## References

- <https://app.hackthebox.com/sherlocks/BlackEnergy>
- <https://attack.mitre.org/software/S0089/>
- <https://github.com/mandiant/capa>
