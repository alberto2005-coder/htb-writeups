---
sherlock: Pwned
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, ransomware, shadow-copies, persistence, timeline]
---

# Pwned — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

A Windows host shows renamed files and a ransom note. The ransomware execution, shadow-copy deletion and scope are reconstructed with EVTX, MFT and registry.

## Scenario

The user cannot open documents and finds a ransom note. Triage artefacts are provided to identify the binary, persistence method and affected data.

## Artefacts

- Ransom note and renamed files.
- EVTX (4688, 7045, 4104).
- `$MFT`, `$UsnJrnl`, prefetch.
- `Run` keys and scheduled tasks.

## Methodology

1. Identify the extension and note; compute hashes.
2. Find the binary in prefetch/MFT and its parent process.
3. Review `vssadmin`, `wbadmin` and PowerShell events.
4. Enumerate services/tasks created before encryption.
5. Scope impact by timestamps and shares.

```bash
EvtxECmd.exe -d C:\\Evidence\\evtx --csv C:\\Evidence\\out
MFTECmd.exe -f C:\\Evidence\\MFT --csv C:\\Evidence\\mft
PECmd.exe -d C:\\Evidence\\prefetch --csv C:\\Evidence\\pf
```

## Sample questions

- Which binary encrypted the files?
- How did it first execute?
- Were shadow copies deleted?
- Which accounts and shares were affected?
- Is persistence still active?

## Tools

`EvtxECmd`, `MFTECmd`, `PECmd`, `Timeline Explorer`, `Volatility`.

## Evidence and redaction

Screenshots of the note, hashes and timeline are kept with users, paths and keys redacted. The note is not published verbatim.

## Lessons learned

- The note and extension provide the first IOC.
- `vssadmin delete shadows` signals ransomware.
- Prefetch/MFT locate the binary even if deleted.
- Persistence may remain after encryption.

## Detection

- Alert on shadow-copy deletion.
- Monitor mass renaming and `README` notes.
- Correlate 4688 with service creation.
- Isolate the host and preserve memory before cleanup.

## References

- <https://app.hackthebox.com/sherlocks/Pwned>
- <https://attack.mitre.org/techniques/T1486/>
- <https://attack.mitre.org/techniques/T1490/>
