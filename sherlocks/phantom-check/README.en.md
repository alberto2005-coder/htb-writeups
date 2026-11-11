---
sherlock: Phantom Check
domain: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, powershell, evtx, wmi, anti-vm, nishang, detection]
---

# Phantom Check — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired according to the writeup and the Operation Blackout 2025 listing; not verified with an HTB session.
> Method note; no literal platform answers.

## Scenario

Talion suspects the attacker performed **anti-virtualization** checks to evade sandboxes. Analyse the PowerShell logs and reconstruct which WMI queries, registry keys and processes were used to detect the environment.

## Evidence

```text
Microsoft-Windows-Powershell.evtx
Windows-Powershell-Operational.evtx
```

```bash
sha256sum *.evtx
EvtxECmd.exe -f Microsoft-Windows-Powershell.evtx --csv out/ --csvf powershell.csv
EvtxECmd.exe -f Windows-Powershell-Operational.evtx --csv out/ --csvf ps-operational.csv
```

KAPE with the `EvtxECmd` module, or `evtx_dump` to JSONL, also works. Preserve each record's channel and `Event ID`.

## Investigation

### 1. Inventory and channels

The two files cover different layers:

- **PowerShell/Operational**: 4103 (module logging) and **4104** (script block logging). 4104 stores the script text, where the anti-VM logic lives.
- **Windows PowerShell** (classic): 400/800 (engine start/stop) and 600 (provider start). They order execution but do not hold the full script.

Filter the 4104 events first and sort by time. A virtualisation-discovery script usually has one function with several checks and a per-platform output.

### 2. WMI queries

The script queries:

- the machine's **model and manufacturer**, to distinguish Hyper-V, VMware, VirtualBox, Xen or QEMU;
- the system **temperature**, a query that often fails in a VM and exposes the environment.

The names documented in the writeups are `Win32_ComputerSystem` for model/manufacturer and `MSAcpi_ThermalZoneTemperature` for temperature. The script does not need to run: 4104 holds the text, and a WMI error event can confirm the query does not exist on the host.

```text
Get-WmiObject -Class Win32_ComputerSystem
Get-WmiObject -Query "SELECT * FROM MSAcpi_ThermalZoneTemperature"
```

### 3. Registry and processes

The script also reads the registry for virtualisation services:

```text
HKLM:\SYSTEM\ControlSet001\Services
```

It compares known process names. For VirtualBox it looks for `vboxservice.exe` and `vboxtray.exe`; for VMware, `vmwareuser.exe`/`vmwaretray.exe`; for Hyper-V, `vmic*` services. Its output uses strings such as `This is a Hyper-V machine` or `This is a VMWare machine`.

The function wrapping the discovery is **`Check-VM`**, adapted from Nishang. That signature is the best rule indicator: it is not one query but a block that tests several platforms.

### 4. Correlation

- 4104 provides the text and `ScriptBlockId`.
- 4103 provides cmdlet invocation and parameters.
- Classic 400/800 give engine start and stop times.
- WMI `Invalid class` errors confirm the temperature query ran on a host without that sensor.

## Conclusions

- The attacker performed **environment awareness** before running the payload: model, temperature, services and processes.
- The logic is in a PowerShell script (`Check-VM`), not a binary, so 4104 is the primary evidence.
- WMI and registry checks are passively observable; no memory or disk is needed.
- Detection should match the whole pattern, not a single string: legitimate scripts may query `Win32_ComputerSystem`.

## Lessons

- **4104 is gold**: without script block logging, the technique is almost invisible.
- Temperature queries are a strong anti-VM indicator because they often do not exist in virtual environments.
- The registry path may be `ControlSet001` or `CurrentControlSet`; rules should cover both.
- An attacker checking the environment has not run the payload yet; blocking here prevents the next step.
- MITRE: T1497.001 (system checks), T1059.001 (PowerShell), T1047 (WMI).
- Mitigation: enable PowerShell script block logging and WMI-Activity, forward events to a SIEM, and alert on `Check-VM`/temperature queries followed by execution.
