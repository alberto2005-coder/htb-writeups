---
sherlock: Unit42
domain: DFIR / Malware
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, sysmon, evtx, ultravnc, timestomp, dropbox, c2]
---

# Unit42 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

A Windows host (`DESKTOP-887GK2L`, user `CyberJunkie`) has a suspicious executable. Only **one Sysmon log** is provided: reconstruct the infection, inspired by Palo Alto Unit 42's UltraVNC backdoor campaign.

## Evidence

```text
sysmon.evtx
```

## Investigation

### 1. From single events to a timeline

```powershell
Get-WinEvent -Path .\sysmon.evtx | Group-Object Id | Sort-Object Count -Descending
```

The Sysmon IDs that matter here:

| ID | Event | What it gives you |
|---|---|---|
| 1 | ProcessCreate | binary, command line, parent, hashes |
| 2 | FileCreateTime changed | **timestomping** |
| 3 | NetworkConnect | outbound IP/port (C2) |
| 5 | ProcessTerminated | dropper exit |
| 11 | FileCreate | files dropped |
| 22 | DNSQuery | domain resolution |

### 2. The binary and its disguise

Filter `EventID 1` and sort by time. The malicious process uses a **double extension** (`*.exe.exe`) and runs from the user's Downloads folder, with Explorer as parent: manual execution, not a service.

The filename is corroborated by `EventID 11`: few files created, all within the same minute.

### 3. Evasion

- **`EventID 2`**: someone changed the binary's creation time. That is timestomping, and it explains why the file "looks old".
- **`EventID 22`**: a DNS lookup before connecting. Droppers resolve a control domain to confirm internet access before contacting the real C2.
- **`EventID 5`**: the dropper exits right after planting the implant. A short-lived process that creates files and dies is a dropper signature, not resident malware.

### 4. The implant

Persistence is not a suspiciously named new service but a **backdoored UltraVNC** variant: it installs as a legitimate service and blends in. Find it by executable path and later `EventID 1` entries, not by signature.

The download source comes from the creation event's URL and the `EventID 22` domain: a cloud storage service (Dropbox) that evades mail filtering.

## Findings

- Delivery: Dropbox link, manual user execution.
- Execution: double-extension binary with prior timestomping.
- Persistence: modified UltraVNC as a legitimate-looking service.
- C2: outbound connection after a DNS connectivity check.

## Lessons

- A single Sysmon channel is enough for a full timeline when IDs 1/2/3/5/11/22 are cross-referenced.
- Timestomping is detected by divergence between `$STANDARD_INFORMATION` and event 2, not by eyeballing dates.
- Sideloading and backdoored "legitimate" services are not caught by signature: catch them by path and time.
