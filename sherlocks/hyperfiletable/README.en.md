---
sherlock: Hyperfiletable
domain: DFIR / Windows
difficulty: Easy
platform: Hack The Box
evidence: A single MFT record from a phished workstation
tools: [MFTECmd, MFTExplorer, Timeline Explorer, hexdump]
---

# Hyperfiletable — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

A new Forela employee downloads their onboarding documents, but a phishing attachment got in the way. From the host only **the MFT record** was recovered: triage the incident with that.

## Evidence

- A `$MFT` (and, depending on the case, its parsed CSV).

## Method

1. **Parse**: `MFTECmd` turns the MFT into CSV.

```bash
MFTECmd.exe -f '$MFT' --csv . --csvf mft.csv
```

2. **User**: the profile with activity is the only real user; its paths (`C:\Users\<user>\...`) confirm it.

3. **Attachment**: look for executables or scripting extensions downloaded by the browser — `.hta`, `.js`, `.lnk` or `.zip` under `Downloads`.

4. **Origin**: the **Zone.Identifier** is an alternate stream (`file:Zone.Identifier:$DATA`). `ZoneId=3` means "downloaded from the Internet"; next to it, `HostUrl` carries the download URL.

5. **Timeline**: `Creation`/`Modified`/`MFTModified` for the download, the attachment and derived files. With only the MFT, timestamps are the whole timeline.

## What it teaches

- The MFT indexes everything that ever existed on the volume: names, sizes, timestamps and attributes.
- `ZoneId=3` proves the file came from the Internet without any browser history.
- `HostUrl` stores the exact download URL: a direct IOC.
- Record size fields (`AllocatedSize`/`RealSize`) reveal slack space and deletions.

## Pitfalls

- **MFT only**: no file contents, so the attachment cannot be hashed.
- **Time zone**: export in UTC and normalise before correlating.
- **Overwritten records**: NTFS reuses records, losing the previous entry.
