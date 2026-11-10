---
sherlock: PhantomRing
domain: Malware analysis / Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [malware-analysis, linux, elf, reverse-engineering, ghidra, c2]
---

# PhantomRing — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Analysis notes; no platform answers.

## Scenario

An alert flagged odd activity on a Linux server. The previous analyst left a sample: an **ELF** run from `/var/tmp` that keeps talking to the outside. Characterise it without detonating it: what it does, who it talks to and how it hides.

## Evidence

```text
phantomring.zip        (password on the Sherlock page)
  └── phantom_ring/agent
```

## Investigation

### 1. Static triage

```bash
file phantom_ring/agent
sha256sum phantom_ring/agent
readelf -h phantom_ring/agent
strings -n 6 phantom_ring/agent | less
```

It is an **ELF x86-64 PIE, dynamically linked** with interpreter `/lib64/ld-linux-x86-64.so.2`, unpacked and **not stripped**: that changes the strategy, because the real function names survive.

```bash
nm phantom_ring/agent | grep ' T \| t '
```

### 2. Symbols: the shortcut

On an unstripped binary, `nm` returns named functions instead of `sub_401230`. Picking the ones that smell of networking, persistence and command execution cuts the analysis to minutes:

```bash
nm phantom_ring/agent | grep -iE 'connect|socket|exec|persist|cmd|port'
objdump -d -M intel --disassemble=<function> phantom_ring/agent | less
```

### 3. The C2 port

The port is not in a table and not encrypted: it appears as an **immediate operand** of the instruction preparing the `connect` structure. Converted from hex to decimal it is the answer, with nothing executed.

### 4. Behaviour

With `Ghidra` (or `objdump`) the flow reconstructs: environment check, connection to the remote host, command read loop and execution (`system`/`popen`), plus an optional persistence routine. IOCs come from here: SHA-256 hash, `/var/tmp` path, process name and C2 endpoint.

### 5. Correlating with the host

```bash
ls -la /var/tmp
grep -R "agent" /etc/cron* /etc/systemd 2>/dev/null
```

Path and running user tell whether it lived as a service, via cron or by hand.

## Findings

- Backdoor-style implant: socket C2 and command execution on the host.
- It runs from a writable temporary directory, the usual way to stay off monitored paths.
- Static analysis alone yields C2, protocol and IOCs; the binary is never executed.

## Lessons

- Executable `/var/tmp` and `/dev/shm` are an indicator by themselves.
- An **unstripped** binary gives function names away: start with `nm`, not the decompiler.
- `strings` plus symbols settle half of a small binary; the port usually sits as an immediate in the code.
- Recording hash, path and endpoint turns the analysis into something detection can act on.
