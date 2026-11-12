---
sherlock: Kawmikaze
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, loader, process-injection, c2, evasion]
---

# Kawmikaze — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original sample or real IOCs.

## TL;DR

An obfuscated loader injects a payload into a legitimate process and contacts a C2. Static, memory and network analysis identify the chain and persistence.

## Scenario

An endpoint generates encrypted traffic to an unknown destination and shows unusual child processes. A sample and memory dump are provided.

## Artefacts

- PE binary, sections and resources.
- Suspicious process memory.
- PCAP/TLS and proxy logs.
- `Run` keys, tasks and services.

## Methodology

1. Identify packer/obfuscation with DIE and `capa`.
2. Review imports and strings for injection APIs.
3. Search memory for executable regions without backing.
4. Correlate the injected process with connections.
5. Extract the payload and document IOCs.

```bash
capa -vv sample.exe
vol.py -f mem.raw malfind
vol.py -f mem.raw netscan
```

## Sample questions

- Which injection technique is used?
- Which process is the target?
- What is the C2 and protocol?
- How does it persist across reboot?
- Which final payload runs?

## Tools

`CAPA`, `Detect It Easy`, `Volatility`, `Procmon`, `Wireshark`.

## Evidence and redaction

Hashes, memory regions and connections are kept with IPs/domains redacted.

## Lessons learned

- Injection leaves regions without file backing.
- A legitimate process hides execution.
- TLS does not prevent correlating destination and process.
- Persistence may be independent of the loader.

## Detection

- Alert on unusual `CreateRemoteThread`/`QueueUserAPC`.
- Monitor processes with RWX regions.
- Correlate connections from unexpected processes.
- Apply YARA in memory.

## References

- <https://app.hackthebox.com/sherlocks/Kawmikaze>
- <https://attack.mitre.org/techniques/T1055/>
- <https://github.com/mandiant/capa>
