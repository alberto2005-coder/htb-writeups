---
sherlock: "OpSalwarKameez24-2: Magic-Show"
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, kape, evtx, memory, rdp]
---

# OpSalwarKameez24-2: Magic-Show — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

StoreD Technologies administrators notice Windows 11 hosts rebooting to apply updates during business hours. Policy allows this only at night. A KAPE triage and a memory dump from one host are provided.

## Evidence

- KAPE output with `C\`, `Windows\System32\winevt` and `$MFT`.
- Memory dump from the affected host.
- Update and RDP session logs.

```bash
tree -L 2 KAPE
sha256sum memory.raw
```

## Investigation

### 1. Inventory and triage

Review Security, System, PowerShell and TerminalServices EVTX. Find the first anomalous logon and compare it with the reboot window. `EvtxECmd` or `Chainsaw` speeds up correlation.

```bash
EvtxECmd.exe -d KAPE/C/Windows/System32/winevt/Logs --csv out
```

### 2. Timeline

A compromised user logs in over RDP and launches `wuauclt` or `UsoClient` outside hours. Service events show installation and reboot. Memory preserves the coordinating process and its connections.

```bash
vol -f memory.raw windows.pslist
vol -f memory.raw windows.netscan
```

### 3. Key artifact

The service creation event and Run key point to a persistence mechanism. The compromised account appears in a type 10 logon and in child processes. Together they explain why updates ran during the day.

## Conclusions

- The reboots were not a Windows Update fault.
- An attacker used a compromised account and RDP.
- Persistence relied on a service or scheduled task.
- Rotate credentials and review the remaining hosts.

## Lessons

- KAPE reduces noise, but validate time and timezone.
- Events 4624 type 10 and 7045 are key.
- Memory and EVTX complement each other.
- An update policy does not stop an attacker from invoking it.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://writeups.chicken0248.fyi/HackTheBox/HTB%20Labs/HTB%20Sherlocks/%5bHTB%20Sherlocks%20Write-up%5d%20OpSalwarKameez24-2%20Magic-Show>
- <https://attack.mitre.org/techniques/T1078/002/>
