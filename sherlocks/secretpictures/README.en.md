---
sherlock: SecretPictures
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware, golang, worm, usb, registry, c2, base64]
---

# SecretPictures — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original sample or real IOCs.

## TL;DR

A Go worm copies itself to USB drives, creates a hidden directory and persists via `Run`. It communicates with a C2 and executes Base64 commands. Static and artefact analysis reconstructs propagation.

## Scenario

Several hosts show a hidden folder and outbound connections. A sample and one host's artefacts are provided to identify the worm and its scope.

## Artefacts

- Go binary and strings.
- `Run`/`RunOnce`, tasks and services.
- `$MFT`, `$Usb` and USBSTOR logs.
- PCAP and files under `%APPDATA%`.

## Methodology

1. Identify Go by sections, imports and strings.
2. Locate USB paths, folder names and `Run` keys.
3. Review USB connection and file-creation events.
4. Decode Base64 commands and extract the C2.
5. Map affected hosts by the same hash.

```bash
strings -n 8 sample.exe | grep -iE 'http|usb|run|base64'
```

## Sample questions

- Which language is it written in?
- Which USB paths does it use to spread?
- Which registry key provides persistence?
- What is the C2 and command format?
- Which hosts show the same IOC?

## Tools

`Detect It Easy`, `Ghidra`, `strings`, `Registry Explorer`, `Wireshark`.

## Evidence and redaction

Hashes, paths and screenshots are kept with IPs, users and filenames redacted.

## Lessons learned

- Go leaves recognizable strings and imports.
- USB worms combine propagation and persistence.
- Base64 is not encryption.
- Scope is measured by hash and artefacts, not names.

## Detection

- Block execution from USB.
- Monitor `Run` and hidden folders.
- Alert on periodic connections.
- Apply YARA by family and hash.

## References

- <https://app.hackthebox.com/sherlocks/SecretPictures>
- <https://attack.mitre.org/techniques/T1091/>
- <https://attack.mitre.org/techniques/T1547/001/>
