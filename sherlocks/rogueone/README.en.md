---
sherlock: RogueOne
domain: DFIR / Memory
difficulty: Easy
platform: Hack The Box
evidence: Memory dump from a Forela workstation
tools: [Volatility 3, windows.netscan, windows.pstree, strings]
state: Retired
tags: [dfir, memory, volatility3, c2, windows]
---

# RogueOne — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method notes; no platform answers.

## Scenario

The SIEM fires several alerts within a minute pointing at possible **C2** from Simon Stark's workstation (Forela). No suspicious process shows in Task Manager, so the SOC isolates the host and hands over a memory dump to confirm the channel and rebuild the timeline.

## Evidence

- A single file: `20230810.mem`, a Windows memory image.

## Investigation

### 1. Processes and tree

```bash
vol -f 20230810.mem windows.pslist
vol -f 20230810.mem windows.pstree
```

`pslist` gives PID, PPID and creation time. An `svchost.exe` **outside `C:\Windows\System32`** — under `Downloads`, say — is the find: legitimate name, illegitimate path.

### 2. Connections

This is the plugin that settles the case:

```bash
vol -f 20230810.mem windows.netscan | grep <PID>
```

It returns an `ESTABLISHED` connection from that PID to an external IP on port **8888**, opened **in the same second** the process was created: the connect-on-start signature.

### 3. Lineage

```bash
vol -f 20230810.mem windows.pstree | grep -A3 <PID>
```

The tree shows `explorer.exe → svchost.exe (fake) → cmd.exe → conhost.exe`: the implant spawns a shell, the mark of an interactive command channel.

### 4. Command line and fingerprint

```bash
vol -f 20230810.mem windows.cmdline --pid <PID>
```

With the path and the executable's SHA-256/MD5 (dumped via `windows.dumpfiles` or `windows.memmap`), look the hash up on VirusTotal; the report gives family and labels. Process creation plus the channel's first packet give the C2 start time.

## Findings

- C2 confirmed from memory: legitimate-looking name, user-writable path, outbound `ESTABLISHED` connection.
- The implant was created and connected in the same second and spawned `cmd.exe`: remote command execution.
- The evidence is endpoint-side: the dump proves the channel even when the EDR saw nothing odd.

## Lessons

- In memory, the binary's path outweighs its name: `svchost.exe` in `Downloads` is malware.
- `netscan` + `pstree` + `pslist` answer "who, where and since when" without disassembling anything.
- Connect-on-start (process created and connection at the same timestamp) is a beaconing indicator.
- The executable's hash is what turns the finding into shareable intelligence.
