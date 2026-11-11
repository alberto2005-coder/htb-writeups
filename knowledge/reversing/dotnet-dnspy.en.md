---
title: ".NET: triage, dnSpy and debugging"
tags: [reversing, dotnet, dnspy, ilspy, windows]
---

# .NET: triage, dnSpy and debugging

**English** | [🇪🇸 Español](dotnet-dnspy.md)

## 1. When to look here

A Windows executable asks for credentials, validates a licence or hides a string. If it is .NET, the intermediate code (CIL) decompiles almost to the original source and analysis stops being archaeology.

## 2. Identify it

```bash
file sample.exe
```

`PE32 executable (GUI) Intel 80386 Mono/.Net assembly` confirms .NET. `strings -el` (UTF-16 strings) and Detect It Easy also help; the latter flags the runtime and any obfuscator.

## 3. Tools

- **dnSpy / dnSpyEx**: decompiler and debugger in one window. Edit-and-continue, breakpoints, locals inspection.
- **ILSpy**: fast decompiler, good IL and resource views.
- **dotPeek**: JetBrains alternative.
- **de4dot**: cleans common obfuscators before decompiling.

Architecture: a 32-bit process needs 32-bit dnSpy; the 64-bit build will not attach. This is the most common mistake.

## 4. Workflow

1. Open the assembly and find the entry point (`Main`) or the button handler.
2. Read the form class: its fields hold the expected values.
3. Break on the final comparison, not on every method.
4. Run with dummy data and read the locals (`this.o`, `this.aa`).
5. Rebuild the condition and document the path.

An example condition that sums up a whole form:

```csharp
if (this.username == this.o && this.check1(s)) { ... }
```

## 5. Obfuscation

Random names, encrypted strings, flattened flow and chained calls are noise. Before chasing them, find the deciding comparison: it is usually one line. `de4dot` recovers names when the protector is known; otherwise the debugger is still enough.

## 6. Limits

- An assembly with anti-tamper or a commercial protector may refuse to run under a debugger; a strong-name signature alone does not prevent debugging. In a CTF, patching the check is fine; in malware, it is not.
- `NativeAOT` and `ReadyToRun` are no longer pure CIL: part of the code is native and needs Ghidra/IDA.
- Embedded resources (`Resources.resx`) may hold the key; check them before concluding.

## 7. Mitigation and detection (real world)

- Never validate credentials client-side: any local comparison can be read with a debugger.
- If a secret is needed, use a public key and verify on the server.
- Detection: assemblies with random names, encrypted strings and P/Invoke to `VirtualAlloc`/`CreateRemoteThread` signal .NET malware; dnSpy and ILSpy are the standard triage.

References: dnSpy, ILSpy and de4dot documentation, and ECMA-335 (CIL).
