---
title: CrownJewel-2
category: DFIR / Active Directory
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, ntds, ntdsutil, esent, evtx]
---

# CrownJewel-2 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

## Scenario

The second round against Forela's DC. In CrownJewel-1 the attacker copied `NTDS.dit` with **`vssadmin`**; now they are back with a domain admin account and this time they use **`ntdsutil.exe`**, which also creates a volume snapshot but leaves traces in the **Application** log of the ESE database.

## Evidence and setup

- `Artifacts/` with `Application.evtx`, `Security.evtx`, `System.evtx` and the NTFS operational log.
- `EvtxECmd` to turn EVTX into CSV, `Timeline Explorer` or `Hayabusa` to filter.
- Timestamps are requested in UTC as `YYYY-MM-DD HH:MM:SS`.

## Method

### 1. The snapshot

`ntdsutil` starts the Volume Shadow Copy service before copying. In `System.evtx` the service enters `running` (event 7036); that mark is when the dump began.

```bash
EvtxECmd.exe -f System.evtx --csv out --csvf system.csv
grep -i "Volume Shadow Copy" out/system.csv
```

### 2. ESE: the three events that give the copy away

The ESE database logs, in **Application**:

- **325** — a new database copy is about to be created (includes the destination path),
- **326** — copy created,
- **327** — database detached and ready for use.

That sequence proves `ntdsutil` rather than `vssadmin`, and it hands over the **full path** of the dumped `ntds.dit`.

### 3. Who, and with what

In `Security.evtx`: `4624` for the compromised domain admin, `4672` (special privileges) for the same `Logon ID`, and `4688` with `ntdsutil.exe`. The `Logon ID` is what joins the three; it identifies the account and the source host.

`ntdsutil` also enumerates groups while it runs: look for **Backup Operators** and **Administrators** queries to confirm the objective.

### 4. Getting the data out

The copy leaves the DC over SMB: `5140`/`5145` against `C$` or `ADMIN$`, or straight to an attacker share. Correlating those with the `325/326` timestamps closes the timeline.

## Findings

The dump used `ntdsutil`, not `vssadmin`: the signature is **7036 (VSS) + 325/326/327 (ESE) + 4688**, and the file path is in event 325 itself. The account is a domain admin, so rotate `krbtgt` twice and hunt the persistence it left.

## Lessons

- `ntdsutil` leaves a triple trace (VSS service, ESENT events, process); `vssadmin` only leaves the service and the binary.
- The `Logon ID` chains `4624` → `4688` → `4672`; without it the events tell no story.
- Event 325 gives the exact dump path, so there is no need to guess from `$MFT`.

## Detection and mitigation

- Restrict `ntdsutil.exe` and `vssadmin.exe` with AppLocker/WDAC and alert on their execution on a DC.
- Tier domain admin accounts, enable `Protected Users` and LAPS.
- Alerts: VSS `7036` followed by `325/326/327` within ten minutes; `5145` on `C$`/`ADMIN$` from non-admin hosts.
- MITRE: T1003.003, T1021.002, T1078.
