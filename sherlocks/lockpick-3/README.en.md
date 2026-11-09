---
sherlock: Lockpick 3.0
domain: Malware analysis
difficulty: Medium
platform: Hack The Box
evidence: Linux binary, memory dump and VM state
tools: [Volatility 3, Ghidra, strings, CyberChef]
---

# Lockpick 3.0 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

The crew behind **Lockpick** has improved: this time it only hit a development server, with no obvious remote access — likely an insider. You are asked to reverse the binary and analyse the host artifacts.

## Evidence

- `ubuntu-client`: the malware.
- `ubuntu-client-Snapshot2.vmem`: memory dump.
- `ubuntu-client-Snapshot2.vmsn`: VM state.

## Method

1. **Identity**: hash and type.

```bash
md5sum ubuntu-client; file ubuntu-client
strings -n 6 ubuntu-client | head -40
```

2. **Obfuscation**: strings are **XOR-encrypted**; find the loop and key in the disassembly or brute-force a single-byte XOR in CyberChef until readable text appears.

3. **Communication**: the binary calls an endpoint (`/connect`) that returns **key, IV and client_id** as JSON; another endpoint uploads files. That is the encryption scheme.

4. **Memory**: **Volatility 3** on the `.vmem` — list processes and command lines (`windows.pslist`/`linux.bash` depending on profile) to see how it was launched and which services it created.

5. **Persistence**: the malware creates and enables a systemd unit (`ubuntu_running.service`): technique **T1543.002**. The `.vmsn` confirms the service state.

## What it teaches

- A single-byte XOR shows up through string entropy and falls by trying keys.
- A `client_id` next to key and IV means symmetric crypto with server-supplied material.
- A memory dump preserves the command line and the services created.
- Comparing `.vmem` and `.vmsn` separates what was in RAM from what was configured.

## Pitfalls

- **Memory profile**: with the wrong symbols Volatility returns nothing; check the kernel version.
- **Encrypted strings**: `strings` is not enough; decrypt or read the disassembly.
- **Do not execute**: analyse statically or in an isolated VM.
