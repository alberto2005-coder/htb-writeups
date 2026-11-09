---
sherlock: Payload
domain: Malware analysis
difficulty: Easy
platform: Hack The Box
evidence: Windows executable with an encrypted payload
tools: [Detect It Easy, x64dbg, PE-bear, CyberChef]
---

# Payload — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

A Windows executable, compiled with **MinGW**, decrypts at runtime the payload it actually executes. Rather than reimplementing the decryption by hand, the exercise walks you through **skipping it with a debugger** and letting the malware do the work.

## Evidence

- One unsigned 32/64-bit `.exe`.

## Method

1. **Static triage**: compiler and sections.

```bash
file sample.exe; strings -n 6 sample.exe | head -40
```

MinGW leaves `gcc`/`mingw` traces and a minimal import table; the payload usually sits in `.rdata`/`.data`.

2. **Entry point**: open in **x64dbg**, go to `EntryPoint` and follow the calls that receive a buffer and a length.

3. **Decryption loop**: usually XOR/RC4/AES over a memory region. Find the instruction writing the decrypted byte and set a **breakpoint after the loop**.

4. **Skip the encryption**: once the buffer is plaintext, dump the region (`Follow in Dump` → `Binary → Save to file`) or flip a jump to execute the decrypted payload.

5. **Analyse the dump**: `strings` and a second debugging pass to uncover the C2 URL, service name or commands.

## What it teaches

- Dynamic execution saves reimplementing algorithms: the malware decrypts for you.
- A breakpoint after the decryption loop is the standard trick against custom packers.
- MinGW binaries carry no signature or metadata: triage starts with the compiler.

## Pitfalls

- **ASLR/PIE**: if the binary relocates, use module-relative addresses.
- **Anti-debugging**: `IsDebuggerPresent`, `NtQueryInformationProcess` or timing checks; patch the branch.
- **Running the payload**: extract and analyse statically, never outside the isolated VM.
