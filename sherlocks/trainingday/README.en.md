---
sherlock: TrainingDay
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware, macro, dropper, powershell, persistence]
---

# TrainingDay — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original sample or real IOCs.

## TL;DR

An Office document with macros downloads and runs a dropper. Static and dynamic analysis identify the payload, persistence and outbound channel.

## Scenario

A user opens an attached document and the host starts generating traffic. The document and execution artefacts are provided to reconstruct the chain.

## Artefacts

- `.docm`/`.xlsm` document.
- VBA macros and obfuscated strings.
- EVTX, prefetch and `%TEMP%`.
- Outbound connection PCAP.

## Methodology

1. Extract macros with `olevba`/`oletools`.
2. Decode strings and locate the download URL.
3. Identify the child process (`powershell`, `mshta`, `rundll32`).
4. Review created files and `Run` keys.
5. Document IOCs and the C2 channel.

```bash
olevba document.docm
strings -n 8 payload.bin
```

## Sample questions

- Which macro runs when the document opens?
- Which URL downloads the payload?
- Which process launches the dropper?
- Where is it stored and how does it persist?
- Which C2 does it contact?

## Tools

`oletools`, `CyberChef`, `Procmon`, `Wireshark`, `PEStudio`.

## Evidence and redaction

Macro screenshots and hashes are kept with URLs, users and paths redacted.

## Lessons learned

- Macros remain an entry vector.
- VBA obfuscation can be reversed patiently.
- The child process reveals execution.
- Persistence usually lives in `Run` keys or tasks.

## Detection

- Block macros from the Internet.
- Alert on Office spawning PowerShell.
- Review downloads to `%TEMP%`.
- Apply YARA to documents and payloads.

## References

- <https://app.hackthebox.com/sherlocks/TrainingDay>
- <https://attack.mitre.org/techniques/T1204/002/>
- <https://attack.mitre.org/techniques/T1059/001/>
