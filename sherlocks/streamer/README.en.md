---
sherlock: Streamer
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, windows, webcache, amcache, shellbags, timeline]
---

# Streamer — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A streaming workstation was compromised and files were deleted. A forensic image with few execution events is provided; the activity must be reconstructed from less obvious artefacts.

## Evidence

- `WebCacheV01.dat`, `Amcache.hve` and `UsrClass.dat`.
- `$MFT`, `$J` and `Windows.edb`.
- Browser history and downloads.

```bash
sha256sum evidence/*
find evidence -iname 'WebCacheV01.dat' -o -iname 'Amcache.hve'
```

## Investigation

### 1. Browsing and downloads

`WECmd`/`ESEDatabaseView` read `WebCacheV01.dat`. Extract URLs, filenames and timestamps; cross-check downloads with the MFT.

```bash
python3 -m pip install --user pyscca
```

### 2. Execution and folders

`Amcache` provides first sightings and hashes. `SBECmd` shows opened folders, including those of the deletion tool. The combination compensates for missing prefetch.

### 3. Reconstruction

Order events and look for gaps: a deleted file leaves traces in USN and MFT. The sequence explains what was downloaded, executed and removed.

## Conclusions

- Browsing reveals the payload origin.
- Amcache and shellbags cover missing prefetch.
- USN shows deletions and renames.
- The timeline is the conclusion, not a by-product.

## Lessons

- "Secondary" artefacts can be primary evidence.
- Deleting a file does not erase every trace.
- Each source has a different time resolution.
- Correlation is mandatory in DFIR.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/EricZimmerman>
- <https://attack.mitre.org/techniques/T1070/004/>
