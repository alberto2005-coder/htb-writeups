---
sherlock: Trojan
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, prefetch, memory, pcap, malware]
---

# Trojan — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A Windows host makes outbound connections after running a supposed installer. A disk image, a memory dump and a network capture are provided.

## Evidence

- `Prefetch`, `Amcache` and `$MFT`.
- `memory.raw` and `capture.pcap`.
- User directory and downloads.

```bash
sha256sum evidence/*
vol3 -f memory.raw windows.info
```

## Investigation

### 1. Execution on disk

`PECmd` confirms the installer and child processes. Compare path and hash with legitimate signatures; `MFTECmd` shows when the file arrived.

```bash
PECmd.exe -d Prefetch --csv prefetch
```

### 2. Memory

Volatility 3 lists processes, connections and modules. A legitimately named process with an anomalous path or unsigned module is the starting point.

```bash
vol3 -f memory.raw windows.pslist
vol3 -f memory.raw windows.netscan
```

### 3. Network

Filter outbound connections and extract domains, JA3 and HTTP. Cross-check the destination with the process and execution time to separate noise from C2.

```bash
tshark -r capture.pcap -Y 'dns or tls.handshake'
```

## Conclusions

- The installer launched an unexpected child process.
- Memory confirms the process and its connection.
- PCAP identifies the C2 destination.
- Path and hash locate the binary.

## Lessons

- Disk, memory and network answer different questions.
- A process name is not enough evidence.
- Volatility needs the right Windows profile.
- Time correlation avoids false positives.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/volatilityfoundation/volatility3>
- <https://attack.mitre.org/techniques/T1204/002/>
