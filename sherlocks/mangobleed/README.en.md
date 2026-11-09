---
sherlock: MangoBleed
domain: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, triage, kape, timeline, persistence]
---

# MangoBleed — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

A logistics company notices odd outbound connections from a workstation. A **triage image** (volatile and disk artefacts) is provided and the job is to find how the attacker got in, what they installed, and what left the network.

## Evidence

- KAPE-style triage: `$MFT`, `UsnJrnl`, registry, `Prefetch`, `Amcache`, event logs.
- The user profile with downloads and recent documents.
- Optionally a memory dump.

## Investigation

### 1. Order of work

Start with what gives temporal context, end with detail:

```text
execution  -> Prefetch, Amcache, UserAssist, SRUM
persistence -> Run keys, scheduled tasks, services, Startup
file access -> LNK, JumpLists, RecentDocs
network -> firewall/proxy logs, DNS cache
```

`PECmd` over `Prefetch` gives first run, run count and binary path; `AmcacheParser` adds hashes and executable metadata.

### 2. Build the timeline

```bash
log2timeline.py --storage-file mango.plaso triage/
psort.py -o l2tcsv mango.plaso "date > '2026-01-01'" > timeline.csv
```

Order is the point: archive download → installer execution → service or task creation → first connections. Any gap in that sequence (execution with no visible download) points to a second vector.

### 3. Persistence

```bash
regipy-dump -o out/ NTUSER.DAT
grep -i "run" out/*.json | head
```

Check `Run`/`RunOnce` (HKCU and HKLM), scheduled tasks (`Windows\System32\Tasks`) and new services. A binary under `%APPDATA%` or `%LOCALAPPDATA%\Temp` referenced from there is the implant.

### 4. Exfiltration

With the tool identified, look for its tracks: staging directories (`.zip`, `.rar` dated to the incident), browser history and connections to a transfer domain. Volume in `SRUM`/firewall answers "how much left".

## Findings

- Access through downloading and running a trojanised installer from the browser.
- Persistence in the user profile, with no administrator rights.
- Data packaged and sent to an external storage service.

## Lessons

- Triage answers nearly everything without memory: execution, persistence and file access all live on disk.
- `Prefetch` + `Amcache` + `UserAssist` is the trio for "what ran and when".
- User-profile persistence evades controls that only watch system services.
