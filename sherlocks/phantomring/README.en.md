---
sherlock: PhantomRing
domain: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [malware-analysis, linux, elf, reverse-engineering, ghidra, c2]
---

# PhantomRing — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Analysis notes; platform answers are not reproduced.

## Scenario

An alert flagged odd activity on a Linux server. The previous analyst left one sample behind: an ELF binary run from `/var/tmp` that appears to keep talking to the outside. Characterise it: what it does, who it talks to, and how it hides.

## Evidence

- The ELF sample (unpacked and stripped, but not heavily obfuscated).
- Host metadata: execution path, launching user, timestamp.
- Optionally, a traffic capture.

## Investigation

### 1. Static triage

Never on the analysis machine without isolation; here, simply do not run it.

```bash
file phantom
sha256sum phantom
readelf -h phantom
strings -n 6 phantom | less
```

`file` confirms architecture and linking (static or dynamic). `strings` usually gives the first lead: URLs, domains, persistence paths and the author's own error messages.

### 2. Imports and behaviour

```bash
readelf -s phantom | grep -E "UND|FUNC"
objdump -d -M intel phantom | less
```

The imported symbols tell most of the story: `socket`, `connect`, `getaddrinfo` mean C2; `fork`, `setsid`, `daemon` mean daemonising; `chmod`, `unlink` mean covering tracks.

### 3. Decompile with Ghidra

Import the binary, accept the auto-analysis and follow references to the interesting strings (`Search > For Strings`, then `References`). `main` typically shows:

1. Argument/environment checks.
2. A connection to the remote host with a fixed token or header.
3. A read-command/execute loop (`popen`/`system`).
4. An optional persistence routine.

The pseudocode rebuilds the protocol: what is sent first, how the implant identifies itself, and the response format.

### 4. Correlate with the host

```bash
ls -la /var/tmp
grep -R "phantom" /etc/cron* /etc/systemd 2>/dev/null
```

The execution path and user answer whether it ran as a service, from cron, or by hand. The IOCs come from here: hash, path, process name, C2 domain/IP.

## Findings

- A backdoor implant with socket C2 and command execution.
- It runs from a writable temporary directory, the usual way to blend in.
- Static analysis alone yields C2, protocol and IOCs; detonation is unnecessary.

## Lessons

- Executable `/var/tmp` and `/dev/shm` are an indicator by themselves.
- `strings` plus imports solve half of a small binary before opening a decompiler.
- Documenting IOCs (hash, path, C2, process) is the real deliverable, not the pseudocode.
