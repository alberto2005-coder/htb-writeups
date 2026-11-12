---
sherlock: Grabber
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, infostealer, static-analysis, dynamic-analysis, iocs]
---

# Grabber — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no original sample or literal answers.

## TL;DR

Analysis of an infostealer/grabber. Static triage, controlled execution and network analysis identify targeted credentials and browsers, where data is staged and how it is exfiltrated. The goal is IOCs and a detection rule.

## Scenario

A user reports account theft after running a downloaded file. A sample or execution artifacts are provided; determine capabilities, persistence and data destination.

## Artifacts

- PE sample (possibly packed).
- Process and network logs.
- Browser/credential artifacts.
- Registry or scheduled-task persistence.
- PCAP or proxy logs.

## Methodology

1. Hash the sample and review headers, imports and strings.
2. Identify packing and deobfuscate if needed.
3. Run it in an isolated VM with process, registry and network monitoring.
4. Observe browser, wallet and credential paths.
5. Locate C2, exfiltration format and persistence.
6. Produce IOCs and Sigma/YARA rules.

```bash
file sample.exe
strings -n 8 sample.exe | head
pefile sample.exe
```

## Sample questions

- Which browser and wallet families does it target?
- Where does it stage data before sending?
- Which domain/IP does it use for exfiltration?
- What persistence does it create?
- Which MITRE ATT&CK techniques apply?

## Tools

`PEStudio`, `Detect It Easy`, `Ghidra`, `x64dbg`, `Procmon`, `Wireshark`, `YARA`.

## Evidence and redaction

Hashes, string captures and traffic are kept with domains and paths redacted. No credentials, keys or flags are published.

## Lessons learned

- Infostealers prioritise browsers and wallets.
- Dynamic execution confirms paths and C2.
- Packing does not prevent strings/import analysis.
- IOCs should include behaviour, not just hashes.

## Detection

- Alert on mass access to `Login Data`, `Cookies` and wallets.
- Monitor processes reading browser profiles.
- Block C2 by domain/IP and proxy.
- Detect persistence in `Run` and scheduled tasks.

## References

- <https://app.hackthebox.com/sherlocks/Grabber>
- <https://attack.mitre.org/techniques/T1555/003/>
- <https://attack.mitre.org/techniques/T1041/>
