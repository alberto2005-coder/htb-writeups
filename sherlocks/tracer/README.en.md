---
sherlock: Tracer
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, psexec, prefetch, mft, lateral-movement, windows]
---

# Tracer — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

The SOC received several **PsExec** alerts on a workstation and escalated them to tier 2. A single endpoint's triage is provided: prove whether the attacker moved laterally, how many times PsExec ran, and which host it came from.

## Evidence

- `PSEXESVC` operational logs (service channel).
- System `Prefetch`.
- MFT table / filesystem artefacts.

## Investigation

### 1. From artefact to executable

```bash
PECmd.exe -d C:/triage/Prefetch -o out/
```

In Timeline Explorer, filter `psexec` and count executions with their timestamps. The service binary PsExec drops is **`psexesvc.exe`**: it shows in `Prefetch`, in the MFT and in the service log as an installed executable (`7045`).

```cmd
wevtutil qe System /q:"*[System[EventID=7045]]" /f:text
```

### 2. Counting executions

Each session logs a start in the service's operational channel. Counting service starts gives the number; confirming they line up with `Prefetch` entries and created files avoids mistaking reconnects for new executions.

### 3. The origin host's fingerprint

PsExec names its artefacts after the source host:

```text
PSEXEC-<HOST>-<PID>.key
\PSEXESVC-<HOST>-<PID>-stderr
\PSEXESVC-<HOST>-<PID>-stdin
```

Searching `*.key` in the triage (or the pipe string in the log) yields the machine that launched the tool. The command line in the service-creation event confirms it with the UNC source path.

### 4. Timeline

Order: service install → `.key` creation → pipe → command execution. One or two seconds apart is normal; minutes apart usually means separate sessions.

```bash
MFTECmd.exe -f C:/triage/$MFT -o out/
```

## Findings

- Tool: PsExec, run several times against the same host.
- Service binary: `psexesvc.exe`, with its `.key` and pipes.
- Origin: host identified by the artefact names and the `7045` command line.

## Lessons

- PsExec leaves three independent traces (service, `.key`, pipe): they agree or the attribution is weak.
- Prefetch and MFT give the "when"; the service log gives the "from where".
- Mitigation: alert on `7045` with binaries in `ADMIN$`, block SMB between workstations, and detect `psexesvc.exe`.
