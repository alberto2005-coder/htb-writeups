---
sherlock: ProcNet
domain: DFIR / Red and endpoint
difficulty: Hard
platform: Hack The Box
evidence: PCAP, API Monitor and Sysmon from a DC and a workstation
tools: [Wireshark, API Monitor, EvtxECmd, Timeline Explorer]
---

# ProcNet — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

The red team simulates an open-source **C2 framework** and hands over what it captured during the exercise: traffic, Windows API calls and Sysmon from both the domain controller and the compromised employee workstation. The goal is to rebuild the chain from endpoint evidence, not just the network.

## Evidence

- Two directories, `DC` and `Employee`, each with a `pcapng`, an **API Monitor** capture (`.apmx64`) and Sysmon logs.

## Method

1. **Which process is talking**: go from the PCAP to Sysmon and identify the binary behind the connection and its parent.

```bash
tshark -r emp.pcapng -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.dst -e tcp.dstport | sort -u
```

```text
EventID 3 (Sysmon) | Image, DestinationIp, DestinationPort
```

2. **Injection and modules**: Sysmon EventID 7 (*ImageLoad*) shows which DLL an unexpected process loads (e.g. a game executable loading a remote-management library).

3. **API Monitor**: the `.apmx64` capture shows the process's actual calls. It confirms **WMI** use (`ExecQueryWmi`, `root\cimv2` connections) and system calls such as `GetFullPathNameW` while staging a download.

4. **Employee to DC**: compare both captures; lateral movement shows as the same binary/DLL running on the other host and in the remote WMI calls.

5. **Timeline**: join Sysmon from both hosts by time and mark first beacon, remote execution and collection.

## What it teaches

- The network says *what* left; the endpoint says *who* did it — correlating both is mandatory.
- API Monitor turns an opaque binary into a call list: intent becomes visible even when packed.
- A remote-administration DLL loaded by a process that does not need it is a lateral-movement signature.

## Pitfalls

- **Legit names**: the process may be named after a game or a common tool; the anomaly is in its modules.
- **Sysmon volume**: filter by `Image` and time window before reading.
- **API Monitor and architecture**: a 64-bit capture will not show a 32-bit process's calls.
