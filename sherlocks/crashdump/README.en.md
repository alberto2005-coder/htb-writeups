---
sherlock: CrashDump
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware-analysis, windows, crash-dump, volatility, memory]
---

# CrashDump — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A Windows server rebooted unexpectedly overnight. The memory dump and some system artifacts were preserved. Determine whether a malicious process caused the crash and reconstruct the preceding activity.

## Evidence

- `MEMORY.DMP` or a full system dump.
- `$MFT`, `$J` and copies of the EVTX logs.
- Process and connection listings from the time of failure.

```bash
sha256sum MEMORY.DMP
vol -f MEMORY.DMP windows.info
```

## Investigation

### 1. Inventory and triage

Identify the Windows version, architecture and dump time. Then list processes, modules and connections to find unexpected names.

```bash
vol -f MEMORY.DMP windows.pslist
vol -f MEMORY.DMP windows.pstree
vol -f MEMORY.DMP windows.netscan
```

### 2. Timeline

Correlate boot times, service events and process timestamps. A process with a legitimate name but a path under `%TEMP%` or `%APPDATA%` is suspicious. Outbound connections to the same destination reinforce the C2 hypothesis.

```bash
vol -f MEMORY.DMP windows.cmdline
vol -f MEMORY.DMP windows.malfind
```

### 3. Key artifact

`malfind` shows `PAGE_EXECUTE_READWRITE` regions with MZ headers and no backing file. Extract the content, hash it and compare it with system files. The injected process and its command line explain the reboot.

## Conclusions

- The crash was not a simple hardware fault.
- A process obtained execution and contacted external infrastructure.
- The dump preserves enough evidence to identify the payload and C2.
- EVTX logs bound the persistence window.

## Lessons

- A crash dump is high-value volatile evidence.
- `malfind` alone does not prove malware; correlate it.
- A file missing from disk does not mean the code never existed.
- Centralize dumps and protect chain of custody.

## References

- <https://www.hackthebox.com/sherlocks/CrashDump>
- <https://github.com/volatilityfoundation/volatility3>
- <https://attack.mitre.org/techniques/T1055/>
