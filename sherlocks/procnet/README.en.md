---
sherlock: ProcNet
domain: DFIR / Red team and endpoint
difficulty: Hard
platform: Hack The Box
evidence: PCAP, API Monitor and Sysmon from a DC and a workstation
tools: [Wireshark, API Monitor, EvtxECmd, Timeline Explorer]
state: Retired
tags: [dfir, c2, sysmon, api-monitor, ja3, lateral-movement]
---

# ProcNet — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method notes; no platform answers.

## Scenario

The red team simulates an **open-source C2 framework** and hands over what was collected during the exercise: traffic, Windows API calls and Sysmon, from both the domain controller and the compromised employee workstation. The goal is to rebuild the chain with endpoint evidence, not network alone.

## Evidence

```text
DC/         pcapng + apmx64 (API Monitor) + Sysmon .evtx
Employee/   pcapng + apmx64 (API Monitor) + Sysmon .evtx
```

## Investigation

### 1. Start with the employee

The brief says the workstation came first. In its `pcapng`, `Statistics → Conversations` leaves two IPs exchanging thousands of packets; the rest is background noise.

```bash
tshark -r Employee.pcapng -q -z conv,tcp
tshark -r Employee.pcapng -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' \
  -T fields -e ip.dst -e tcp.dstport | sort -u
```

### 2. Identify the implant and the framework

Sysmon **EventID 1** (process creation) and **EventID 3** (network connection) tie binary to destination. For the framework, the distinguishing datum is the client TLS **JA3 fingerprint**: every C2 library negotiates with a specific one.

```bash
tshark -r Employee.pcapng -Y 'tls.handshake.type==1' \
  -T fields -e ip.dst -e tls.handshake.ja3 | sort -u
```

JA3 plus the beacon pattern (regular interval, constant request size) identifies the framework family, confirmed against endpoint telemetry.

### 3. API Monitor: intent

The `.apmx64` shows the process's real calls even when the binary is packed. Here the revealing part is **credential enumeration**: Windows Vault API calls (enumerate vaults, read items) appear inside the attacker's process, not in an admin tool.

```text
API Monitor → filter: VaultEnumerateVaults, VaultEnumerateItems, CryptUnprotectData
```

That upgrades "C2" to "C2 with credential theft", which explains the jump to the DC.

### 4. From the employee to the DC

Repeat with `DC/pcapng`: same binary or DLL on the other host, same calls, and Sysmon **7 (ImageLoad)** showing a remote-administration library loaded by a process that has no business using it (a game-named binary, for example).

### 5. Timeline

Join both hosts' Sysmon by UTC hour: first beacon on the employee, vault enumeration, implant appearing on the DC, collection afterwards. The interval between beacons gives the C2 periodicity.

## Findings

- The framework is identified by **JA3 + beacon cadence**, not by process name.
- API Monitor proves **credential access** from the implant, the bridge to the domain controller.
- The chain rests on two sources: network (where) and endpoint (who and with which calls).

## Lessons

- In a red-team exercise the question is not "is there C2?" but "what did the C2 do on the host?".
- JA3 survives encryption and collapses thousands of flows into one fingerprint; the best shortcut when the payload is opaque.
- API Monitor turns an opaque binary into a list of intentions; Vault means credentials, not "odd activity".
- Filter Sysmon by `Image` and time window before reading: volume is the enemy.
- A 64-bit capture shows no calls from a 32-bit process: check architecture before concluding "nothing there".
