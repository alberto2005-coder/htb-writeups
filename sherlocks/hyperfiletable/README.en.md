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

- A `$MFT` compressed with **bzip2** (decompress before parsing; the MD5 the challenge asks for is the one of the decompressed `$MFT`, not of the archive).

## Method

1. **Parse**: `MFTECmd` turns the MFT into CSV.

```bash
MFTECmd.exe -f '$MFT' --csv . --csvf mft.csv
```

2. **User**: the profile with activity is the only real user; its paths (`C:\Users\<user>\...`) confirm it.

3. **Attachment**: here it is an **`.hta`** downloaded from a Google-Drive-style link, next to a legitimate PowerPoint used as bait. Look for executables or scripting extensions under `Downloads`.

4. **Origin**: the **Zone.Identifier** is an alternate stream (`file:Zone.Identifier:$DATA`). `ZoneId=3` means "downloaded from the Internet"; next to it, `HostUrl` carries the download URL.

5. **Timeline**: `Creation`/`Modified`/`MFTModified` for the download, the attachment and derived files. With only the MFT, timestamps are the whole timeline.

## Findings

The new joiner downloaded a malicious `.hta` from an external link and ran it: the MFT keeps the path, the `Zone.Identifier` with `ZoneId=3` and the `HostUrl` of the download, and the gap between real and allocated size exposes the file and its remains.

## What it teaches

- The MFT indexes everything that ever existed on the volume: names, sizes, timestamps and attributes.
- `ZoneId=3` proves the file came from the Internet without any browser history.
- `HostUrl` stores the exact download URL: a direct IOC.
- Record size fields (`AllocatedSize`/`RealSize`) reveal slack space and deletions.

## Pitfalls

- **MFT only**: no file contents, so the attachment cannot be hashed.
- **Time zone**: export in UTC and normalise before correlating.
- **Overwritten records**: NTFS reuses records, losing the previous entry.
