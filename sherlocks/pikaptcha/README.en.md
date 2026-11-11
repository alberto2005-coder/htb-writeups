---
sherlock: Pikaptcha
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, pcap, kape, registry, runmru, powershell, clipboard]
---

# Pikaptcha — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal platform answers.

## Scenario

A user opens a link claiming to be an Office update and solves a fake captcha. The clipboard ends up holding a PowerShell command that downloads a script and opens a reverse shell. The organisation provides a nearly 500 MB packet capture and a KAPE triage of the host; the job is to reconstruct the sequence and the binary that ran.

## Evidence

```text
Pikaptcha/pikaptcha.pcapng                                  full capture of the incident
Pikaptcha/2024-09-23T052209_alert_mssp_action.zip           KAPE 1.3.0.2 triage
  C/Users/<user>/NTUSER.DAT (+ .LOG1/.LOG2, UsrClass.dat)
  C/Windows/prefetch/*.pf
  C/Windows/System32/sru/SRUDB.dat
  _CopyLog.csv, _SkipLog.csv
```

```bash
sha256sum pikaptcha.pcapng *.zip      # record before analysing
regipy-process-transaction-logs NTUSER.DAT -p NTUSER.DAT.LOG1 -s NTUSER.DAT.LOG2
```

The hive is dirty: without replaying the transaction logs the last written keys are lost, and those are exactly the incident's keys.

## Investigation

### 1. Inventory and triage

Start with the capture, because it gives the order of events and the downloaded objects. In Wireshark, `File → Export Objects → HTTP` recovers the captcha page and the `.ps1`. Then work the hive: `regipy-dump NTUSER.DAT.restored > NTUSER.json` and search for `powershell`, `RunMRU` and `Console`.

```bash
tshark -r pikaptcha.pcapng -Y 'http.request' -T fields -e frame.time -e ip.dst -e http.host -e http.request.uri | head
```

### 2. Timeline

Capture time and artefact time agree in UTC; no conversion needed. The sequence is: link click, captcha page, `stageClipboard()` copying the command, execution from the `Win+R` dialog (recorded in `RunMRU`), and download of `office2024install.ps1` from `43.205.115.44`. The script decodes a base64 string and opens a connection to `43.205.115.44:6969`, active between 05:07:48 and 05:14:31.

### 3. Key artefact

`RunMRU` proves the command ran from the clipboard and not from a console: the entry keeps the full `IEX(New-Object Net.WebClient).DownloadString(...)` command. Prefetch `.pf` files confirm `powershell.exe` and `curl.exe` running in the same window, and `SRUDB.dat` adds the process start time.

```bash
grep -o '"[^"]*powershell[^"]*"' NTUSER.json | head
```

The hash of the exported `.ps1` is recorded as an IOC and compared with the one in the capture.

## Conclusions

- Entry: social engineering with a fake captcha abusing the clipboard; the command is run manually from `Win+R`.
- Execution: PowerShell downloads and runs a remote script, then a base64 reverse shell.
- C2: `43.205.115.44`, port 80 for the download and 6969 for the shell.
- Persistence: none observed; the active window is about seven minutes.
- IOCs: `.ps1` hash, server IP, script path and the `RunMRU` entry.

## Lessons

- The clipboard is an execution channel: a "Copy" button writing PowerShell plus a captcha asking you to paste it into `Win+R` is the whole chain.
- A hive with `.LOG1`/`.LOG2` hides the newest keys unless replayed; `regipy` or Registry Explorer is mandatory.
- The capture recovers the script even if the EDR deleted it from disk.
- Mitigation: block execution from `RunMRU` for standard users, restrict PowerShell to constrained language mode and alert on `IEX` with download.
- Detection: `4104` with `DownloadString`, `4688` for `powershell.exe` with `-nop -w hidden`, outbound connections to IPs with no reputation, and `RunMRU` holding `powershell`.
- What is missing: Sysmon `DNS` and `NetworkConnect` telemetry to tie process and connection together.

MITRE: T1204.002 (malicious file), T1059.001 (PowerShell), T1105 (ingress tool transfer), T1071.001 (web protocols).
