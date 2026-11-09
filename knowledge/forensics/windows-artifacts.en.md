---
title: Windows artifacts — EVTX, MFT, Prefetch and Sysmon
tags: [forensics, windows, dfir, evtx, mft, sysmon]
---

# Windows artifacts: what to look at and with what

**English** | [🇪🇸 Español](windows-artifacts.md)

## 1. Order of work

1. **Timeline** of execution and logons (Prefetch, EVTX, MFT).
2. **Persistence** (services, tasks, Run keys, WMI).
3. **Lateral movement** (4624 type 3/10, 5140, SMB, RDP).
4. **Exfiltration** (Sysmon 3, DNS, browser).

Reference tools: Eric Zimmerman's suite (`EvtxECmd`, `MFTECmd`, `PECmd`, `AmcacheParser`, `AppCompatCacheParser`) and `Timeline Explorer` to correlate. `Hayabusa` summarises EVTX with Sigma rules.

## 2. EVTX: the events that matter

| Event | What it says |
|---|---|
| 4624 | successful logon; **type 3** network, **type 10** RDP |
| 4625 | failed logon (brute force, spray) |
| 4648 | explicit credentials (`runas`) |
| 4672 | special privileges assigned |
| 4688 | process created (with command line when enabled) |
| 4720/4732 | user created / added to group |
| 4769 | TGS requested (RC4 `0x17` = Kerberoasting) |
| 4662 | AD object access (DCSync: `DS-Replication-Get-Changes`) |
| 5140/5145 | share access |
| 7045 | service installed |
| 4698 | scheduled task created |
| 4104 | PowerShell script block |
| 1102 | log cleared |

```bash
EvtxECmd.exe -d C:\Evidence\Windows\System32\winevt\Logs --csv C:\Out --csvf evtx.csv
Hayabusa.exe csv-timeline -d C:\Evidence\Logs -o timeline.csv
```

## 3. MFT and timestamps

`$MFT` gives name, size, flags and four timestamps per file. `MFTECmd` turns it into CSV:

```bash
MFTECmd.exe -f '$MFT' --csv C:\Out --csvf mft.csv
```

- **Timestomping**: `$STANDARD_INFORMATION` earlier than `$FILE_NAME`, or both inconsistent with `$LogFile`/`UsnJrnl`.
- **Zone.Identifier**: ADS holding the source URL of a downloaded file.
- **Resident files**: content inside the MFT entry itself (handy for small scripts).

## 4. Execution and persistence

- **Prefetch** (`PECmd`): executables, run count, last run, files opened.
- **Amcache**: executables and hashes seen.
- **Shimcache/AppCompatCache**: executables that existed, without reliable dates.
- **Run keys**: `HKLM\...\CurrentVersion\Run`, `RunOnce`, tasks (`.job`), services (`ImagePath`).
- **WMI**: subscriptions under `root\subscription` (fileless persistence).
- **PSReadLine**: `ConsoleHost_history.txt` with the user's commands.

## 5. Correlation

One artifact proves nothing. Typical pattern:

```text
Prefetch of powershell.exe  →  4104 with the script  →  4688 of the child  →  5140 to the share
```

Always cross **two sources** and record the exact path of each piece of evidence. In Sherlocks, the answer is usually in the cross-check, not in a single event.

## 6. Typical errors

- **`EvtxECmd` cannot read an `.evtx`** → corrupt or from another version; try `wevtutil epl` from Windows.
- **UTC and local dates mixed** → normalise everything to UTC before comparing.
- **`$MFT` without names** → you also need `$UsnJrnl` or `$LogFile` to resolve renames.
- **Empty Prefetch** → Prefetch was off or the SSD policy disabled it.
- **"Perfect" timestomp** → check `$FILE_NAME` and MFT entry order, not just `$STANDARD_INFORMATION`.

## 7. Detection and mitigation

- Enable process auditing (4688 with command line), PowerShell (4104) and Sysmon.
- Centralise EVTX with forwarding and enough retention.
- Monitor 7045/4698 and Run key changes; alert on 1102.
- Use `$MFT` + `UsnJrnl` for timestamp integrity.

MITRE: T1070.006 (timestomp), T1059.001, T1543, T1053.
