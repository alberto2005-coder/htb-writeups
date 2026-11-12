---
sherlock: Oxide
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, memory, process-injection, volatility, malware]
---

# Oxide — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

A Windows memory dump contains an injected process and C2 connections. `pstree`, `malfind`, `netscan` and `dlllist` identify the injection, payload and persistence.

## Scenario

A host shows slowness and intermittent outbound connections. A memory dump is provided to identify the malicious process and its command channel.

## Artefacts

- Full memory (`memdump.mem`/`.raw`).
- `pstree`, `malfind`, `netscan`.
- `dlllist`, `handles`, `cmdline`.

## Methodology

1. Identify the profile with `imageinfo`.
2. Review orphan processes and anomalous parent-child relations.
3. `malfind` locates executable regions without a disk backing.
4. `netscan` correlates connections with processes.
5. Extract strings and hash the payload.

```bash
vol.py -f memdump.mem imageinfo
vol.py -f memdump.mem --profile=Win10x64_19041 pstree
vol.py -f memdump.mem --profile=Win10x64_19041 malfind
vol.py -f memdump.mem --profile=Win10x64_19041 netscan
```

## Sample questions

- Which process is injected?
- Which DLL or region is anomalous?
- Which C2 does it connect to?
- Which process launched it?
- Is there persistence in memory?

## Tools

`Volatility 2/3`, `MemProcFS`, `strings`, `YARA`.

## Evidence and redaction

Screenshots of processes, regions and connections are kept with IPs, users and paths redacted.

## Lessons learned

- Injection leaves executable regions with no file backing.
- `netscan` links process and connection.
- Orphan processes betray malware.
- Memory complements disk when the binary is missing.

## Detection

- Alert on processes with `PAGE_EXECUTE_READWRITE` regions.
- Monitor connections from unexpected processes.
- Correlate injection with network access.
- Apply YARA in memory.

## References

- <https://app.hackthebox.com/sherlocks/Oxide>
- <https://attack.mitre.org/techniques/T1055/>
- <https://github.com/volatilityfoundation/volatility3>
