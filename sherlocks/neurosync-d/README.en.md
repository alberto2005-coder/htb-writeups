---
sherlock: NeuroSync-D
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, medical-device, timeline, lateral-movement]
---

# NeuroSync-D — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

The maker of a connected medical device (a neural interface) notices anomalous activity on a technician's workstation. Endpoint artefacts and network logs are provided; the job is to establish how access was gained, what was manipulated, and whether the incident reached other systems.

## Evidence

- Endpoint artefacts: registry, `Prefetch`, `Amcache`, PowerShell history.
- Authentication and network logs from the lab segment.
- The vendor's device and software inventory.

## Investigation

### 1. Entry point

```bash
PECmd.exe -d triage/Prefetch --csv out/
grep -i "powershell" out/*.csv | head -20
```

Typical indicators are an executable downloaded to `Downloads` followed by `powershell -enc` in the same time window. The console history (`ConsoleHost_history.txt`) often keeps the full command.

### 2. What happened to the device

Cross the execution time with the clinical software logs: configuration reads, patient-data exports or firmware changes. In this scenario the point is not the malware but the **access to regulated data**.

### 3. Scope

```bash
grep -i "4624\|4625\|4648" Security.evtx | head
```

Review type 3/10 logons from the compromised host to other machines and use of service credentials. Scope closes with the systems that shared the account.

## Findings

- Compromise of a lab workstation with access to medical-device data.
- Lateral movement limited by segmentation, but sensitive information exposed.
- Impact measured in compliance (health data), not just flags.

## Lessons

- In regulated environments, start from which data was touched, not from which binary ran.
- Network segmentation is what separates an incident from a disaster when the endpoint falls.
- Chain of custody and hashes are part of the deliverable.
