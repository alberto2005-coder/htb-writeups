---
sherlock: Ghost Thread
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, api-monitor, process-injection, shellcode]
---

# Ghost Thread — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

An analyst suspects the attacker injected code into a legitimate process to avoid disk artefacts. An API Monitor capture and an IDA database of the injector are provided; identify the technique, calls and target process.

## Evidence

- `capture.apmx64` and its data directory.
- `inject.exe.i64` for IDA.
- Incident description and guiding questions.

```bash
unzip capture.apmx64 -d capture
find capture -maxdepth 3 -type f
```

## Investigation

### 1. Inventory

The capture is a ZIP with `log/monitoring.txt` and raw call data. Keep a copy and record the hash before opening it.

```bash
sha256sum capture.apmx64 inject.exe.i64
```

### 2. Win32 calls

Look for injection APIs: process snapshot, process open, memory allocation, write and remote thread creation. Order and arguments identify the variant.

```text
CreateToolhelp32Snapshot -> Process32First/Next -> OpenProcess
VirtualAllocEx -> WriteProcessMemory -> CreateRemoteThread
```

### 3. Process and payload

The target process name comes from the injector's comparison and the `PID` in the call. In IDA, review the function that runs before `main` and the shellcode size.

## Conclusions

- The sequence is classic remote-thread injection.
- The target is a legitimate editor, not a system service.
- The payload runs in memory and avoids disk.
- The API Monitor capture is enough to rebuild the chain.

## Lessons

- API Monitor shows calls without running the sample.
- API order matters as much as their names.
- A legitimate process can hide malicious code.
- IDA complements the capture for shellcode size and origin.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex>
- <https://attack.mitre.org/techniques/T1055/002/>
