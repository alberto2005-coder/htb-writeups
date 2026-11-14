---
sherlock: SillyEli
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, windows, srum, ese, powershell, scheduled-tasks]
---

# SillyEli — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A Windows server shows after-hours network activity and processes. A KAPE collection is provided, and the task is to identify the executable, persistence and exfiltrated volume.

## Evidence

- `SRUM` (`SRUDB.dat`) and `Windows.edb`.
- Scheduled tasks, services and PowerShell.
- `$MFT`, `Prefetch` and Security logs.

```bash
sha256sum evidence/*
find evidence -iname 'SRUDB.dat' -o -iname 'Windows.edb'
```

## Investigation

### 1. Usage and network

`SrumECmd` extracts bytes sent/received per process and time. A process with high traffic in a specific window guides the search.

```bash
SrumECmd.exe -f SRUDB.dat --csv srum
```

### 2. Execution and persistence

`PECmd` confirms execution; scheduled tasks and services explain persistence. `Windows.edb` may preserve user paths and searches.

```bash
PECmd.exe -d Prefetch --csv prefetch
```

### 3. PowerShell and scope

Review 4103/4104 and transcripts. Cross-check the download or compression command with SRUM and the MFT to estimate what was packaged and sent.

## Conclusions

- SRUM provides volume and a time window.
- Persistence is confirmed by tasks or services.
- PowerShell documents the command and user.
- Exfiltration estimates rely on two sources.

## Lessons

- SRUM helps when network logs are missing.
- ESE may be locked; work on a copy.
- Scheduled tasks leave traces in several artefacts.
- Volume attribution is an estimate, not certainty.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/EricZimmerman/Srum>
- <https://attack.mitre.org/techniques/T1053/005/>
