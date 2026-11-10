---
sherlock: Lockpick 3.0
domain: Malware analysis
difficulty: Hard
platform: Hack The Box
evidence: Linux ELF, memory dump and VM state
tools: [Volatility 3, Ghidra, strings, CyberChef]
state: Retired
tags: [dfir, malware, ransomware, linux, xor, systemd, memory]
---

# Lockpick 3.0 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

The **Lockpick** crew has improved: this time it only hit a development server, with no obvious remote access — likely an insider. You are asked to reverse the binary and analyse the host artifacts.

## Evidence

- `ubuntu-client`: the malware (ELF, MD5 `a2444b61b65be96fc2e65924dee8febd`).
- `ubuntu-client-Snapshot2.vmem`: memory dump.
- `ubuntu-client-Snapshot2.vmsn`: VM state.

## Investigation

1. **Identity**: `md5sum` and `file`; this is a Linux ELF, so `objdump -d`/Ghidra, not Windows tooling.

2. **Encrypted strings**: the binary hides its configuration behind a **repeating XOR**. The key is **not in the file**: it is passed on the command line (`./ubuntu-client <key>`). That is why `strings` on the binary is not enough and the `.vmem` matters — the process command line keeps the key.

```bash
strings -n 8 ubuntu-client-Snapshot2.vmem | grep ubuntu-client
```

3. **Decrypt**: with the key from the command line, invert the XOR over the data section and the C2 base URL, the endpoints (`/connect` for key/IV/`client_id`, `/uploads/` for exfiltration) and a full systemd unit appear.

4. **Communication**: `_cJSON_GetObjectItem` confirms `/connect` answers JSON with the crypto material; `client_id` identifies the victim.

5. **Persistence**: the malware writes and enables `ubuntu_running.service` under `/etc/systemd/system` (technique **T1543.002**). The `.vmsn` confirms the service state and the `.vmem` the running process.

## Findings

- C2 hosted on a PaaS (`*.ondigitalocean.app`), which makes IP blocking hard.
- Server-supplied key material: symmetric crypto with remote secrets.
- Persistence through a systemd unit the binary creates itself.

## Lessons

- If the key travels as an argument, the binary does not leak it: memory does.
- A repeating XOR breaks as soon as the key is known; finding it is the challenge.
- Comparing `.vmem` and `.vmsn` separates what was in RAM from what was configured on disk.

## Pitfalls

- **Memory profile**: this is Linux; use `linux.bash`/`linux.pslist`, not Windows plugins.
- **Obfuscated strings**: `strings` on the ELF shows no config; decrypt it.
- **Do not execute**: static analysis or an isolated VM.
