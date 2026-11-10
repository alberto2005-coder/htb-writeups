---
sherlock: Payload
domain: Malware analysis
difficulty: Easy
platform: Hack The Box
state: Retired
evidence: Windows executable with a runtime-decrypted payload
tools: [PEStudio, radare2, x64dbg, Detect It Easy]
tags: [malware, windows, mingw, unpacking, x64dbg]
---

# Payload — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Analysis notes; no platform answers.

## Scenario

First day after training: a suspicious binary arrives and you must say what it does without running it in production. The executable shows a harmless dialog and **decrypts in memory** the payload that actually matters.

## Evidence

- A single file: **`func_pointer.exe`**.

## Investigation

### 1. Static triage

```bash
file func_pointer.exe
rabin2 -I func_pointer.exe      # or radare2 -I: arch, bits, protections, timestamp
```

- The binary is compiled with **MinGW** (GCC for Windows): compiler strings and a minimal import table give it away.
- Running it only pops a dialog reading `HTB pwned us`: the functionality sits behind a decryption routine.
- The PE header timestamp and the compiler are the first two answers asked for.

### 2. Where the payload is

The binary uses **function pointers**: it takes an encrypted buffer, decrypts it in memory and jumps to it. In `x64dbg`:

1. Load, run to the user entry point (`Run to user code`).
2. Find the call receiving a buffer and a length, plus the loop writing byte by byte with `XOR` (or a small block cipher).
3. Set a **breakpoint after the loop**: at that point the buffer is plaintext.

### 3. Extract the second stage

```text
Follow in Dump → select the region → Binary → Save to file
```

The dump holds the decrypted payload. The task asks for **the address** where it landed and its content: `strings` on the dump reveals the C2 URL, service name or commands.

### 4. Verification

- `PEStudio` on the dump tells whether it is a full PE or shellcode.
- Compare hashes of the original and the dump: they must differ (encrypted vs plaintext).

## Findings

- The binary is a *loader*: it does not attack by itself, it delivers the next stage.
- The encryption is reversible **on the host**; there is no need to reimplement the algorithm.
- The decrypted buffer address is an analysis datum, not an internal detail.

## Lessons

- Against a home-made packer, the debugger does the work: run until the malware decrypts itself.
- `MinGW` + minimal imports + a decoy dialog is a loader profile, not an application.
- The PE header timestamp is unreliable as proof of compilation but useful as a hint.
- Never launch the second stage outside an isolated, network-less VM.
