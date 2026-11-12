---
sherlock: Artifact
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, mft, archives, timeline, exfiltration]
---

# Artifact — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

The creation and transfer of a compressed archive with sensitive data is investigated. MFT, prefetch, LNK and network logs reconstruct what was compressed, when, and how it left the host.

## Scenario

An organisation suspects an employee packaged information before leaving. A partial image is provided to reconstruct the preparation and exfiltration.

## Artefacts

- `$MFT` and `$UsnJrnl`.
- Prefetch, LNK and jumplists.
- Firewall/proxy logs.
- PowerShell history.

## Methodology

1. Look for `.zip`/`.7z`/`.rar` files created in the period.
2. Review MFT and USN timestamps for creation order.
3. Confirm compressor execution with prefetch.
4. Review LNK/jumplists for source files.
5. Correlate with outbound connections and cloud services.

```bash
MFTECmd.exe -f C:\\Evidence\\MFT --csv C:\\Evidence\\mft
PECmd.exe -d C:\\Evidence\\prefetch --csv C:\\Evidence\\pf
```

## Sample questions

- Which archive was created?
- Which files does it contain?
- Which tool was used?
- When was it created and modified?
- Was it uploaded to an external service?

## Tools

`MFTECmd`, `PECmd`, `LECmd`, `Timeline Explorer`, `Wireshark`.

## Evidence and redaction

Screenshots of the timeline and hashes are kept with usernames, paths and destinations redacted.

## Lessons learned

- The MFT preserves creation, modification and access.
- Compressors leave prefetch traces.
- LNK files reveal selected source files.
- Exfiltration needs network correlation.

## Detection

- Alert on bulk document compression.
- Monitor uploads to personal storage.
- Correlate MFT with outbound traffic.
- Review after-hours access.

## References

- <https://app.hackthebox.com/sherlocks/Artifact>
- <https://attack.mitre.org/techniques/T1560/001/>
- <https://attack.mitre.org/techniques/T1048/>
