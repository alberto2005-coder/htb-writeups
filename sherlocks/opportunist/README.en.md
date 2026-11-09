---
sherlock: Opportunist
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, memory, volatility, rat, browser-forensics, kill-chain]
---

# Opportunist — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

A finance user opens an email attachment and, hours later, the host starts sending traffic to an unknown VPS. A **memory dump**, a disk triage and the browser cache are provided. Rebuild the full chain: delivery, execution, persistence and exfiltration.

## Evidence

- `memory.raw` (full dump).
- Triage: registry, `Prefetch`, `Amcache`, `$MFT`.
- Browser cache and downloads.

## Investigation

### 1. System picture from memory

```bash
vol -f memory.raw windows.info
vol -f memory.raw windows.pslist | tee pslist.txt
vol -f memory.raw windows.pstree
vol -f memory.raw windows.cmdline
```

Randomly named processes under `%APPDATA%` or `%TEMP%`, unsigned and with an empty command line, are the candidates. `pstree` reveals the parent: an `explorer.exe` launching a binary from `Downloads` means the user double-clicked it.

### 2. Connections and C2

```bash
vol -f memory.raw windows.netscan | grep ESTABLISHED
vol -f memory.raw windows.dlllist --pid <PID>
```

`netscan` gives remote IP/port and process; the PID confirms the connection belongs to the implant rather than the browser. DLLs loaded from user paths (`AppData`) inside a system process indicate injection.

### 3. Execution and persistence on disk

```bash
PECmd.exe -d triage/Prefetch --csv out/
AmcacheParser.exe -f triage/Amcache.hve --csv out/
regipy-dump -o out/ triage/NTUSER.DAT
```

Cross the first run with the time of the email/download. Typical opportunistic RAT persistence: a HKCU `Run` value pointing at `%APPDATA%\Roaming\<folder>\<binary>.exe`, or a scheduled task named like an update.

### 4. User activity and exfiltration

```bash
python3 chrome_cache.py triage/Default/Cache
sqlite3 triage/Default/History "select url, last_visit_time from urls order by last_visit_time desc limit 20;"
```

The browser cache keeps the downloaded file and its origin; history gives the download time. With that window, look for archives created afterwards and correlate them with `netscan` traffic.

## Findings

- Delivery as a browser download of a file the user ran manually.
- A RAT with VPS C2, profile-level persistence and command execution.
- Financial data packaged and sent over the same channel.

## Lessons

- Memory answers "what was running and who it talked to"; disk answers "how it arrived and how it comes back".
- The parent process is the evidence of exploit versus human error.
- An opportunistic RAT needs no 0-day: attachment + double click + `Run` key.
