---
sherlock: CAMouflage
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, kape, prefetch, mft, usn]
---

# CAMouflage — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A Windows workstation shows executables named like legitimate utilities. A disguised installer may have run and left persistence; a KAPE collection is provided.

## Evidence

- `Prefetch`, `Amcache.hve` and `SRUM`.
- `$MFT`, `$J` and `AppCompatCache`.
- User folders and downloads.

```bash
sha256sum evidence/* 2>/dev/null | head
find evidence -maxdepth 2 -type d
```

## Investigation

### 1. Execution triage

`PECmd` lists executables and run times. Compare lookalike names against path and hash; a binary in `%TEMP%` or `Downloads` is suspicious.

```bash
PECmd.exe -d evidence/Prefetch --csv prefetch
```

### 2. Creation correlation

`MFTECmd` reconstructs file creation and modification. `Amcache` provides first sighting and SHA-1; `SRUM` confirms network or CPU use.

```bash
MFTECmd.exe -f '$MFT' --csv mft
```

### 3. Persistence and scope

Review Run keys, tasks and services. Cross-check the executable path with prefetch and USN to learn whether it was copied, renamed or run repeatedly.

## Conclusions

- The file name does not identify the tool.
- Prefetch, Amcache and MFT confirm execution and origin.
- Persistence is validated with the registry and tasks.

## Lessons

- Camouflage is detected by path, signature and hash.
- Execution artefacts have different lifetimes.
- The MFT helps reconstruct copies and renames.
- Separate installation from execution.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/EricZimmerman/PECmd>
- <https://attack.mitre.org/techniques/T1036/005/>
