---
challenge: Find The Easy Pass
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, dotnet, dnspy, decompilation]
---

# Find The Easy Pass — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The executable is .NET and validates the password with a direct comparison. `dnSpy` or `ILSpy` decompile the method and reveal the expected string and the flag.

## Prompt and surface

- Reversing, Very Easy, retired.
- A Windows `.exe` is provided.
- The prompt asks for the password.

```bash
file EasyPass.exe
strings -el EasyPass.exe | head
```

## Reconnaissance

- `file` identifies a .NET PE.
- `strings` shows method names and UTF-16 strings.
- No obvious packing.

## Code analysis

Open the assembly in `dnSpy` and find `Main` or the button handler. The method compares input with a constant through `String.op_Equality` or `Equals`.

The flag is derived from the password or printed in the success branch.

## Why it works

Validation happens client-side and the password is embedded. There is no derivation or remote check: decompilation reveals the secret.

## Local reproduction

```bash
# Windows
EasyPass.exe
# Decompile with dnSpy/ILSpy
```

- Find the validation method.
- Break on the comparison.
- Read the constant and the call that prints the flag.

## Exploitation

Enter the recovered password and the program prints the flag. The conditional jump can also be patched to accept any input.

## Evidence

- `file` output and `dnSpy` screenshot.
- Redacted comparison string.
- Successful run without the flag.

## Lessons learned

- .NET keeps metadata and names.
- A secret in the client is not a secret.
- Breakpoints reveal the comparison without patching.

## Mitigations and detection

- Validate licences on the server.
- Obfuscation is an extra layer, never the only protection.
- Sign the binary and verify integrity.

## References

- <https://www.hackthebox.com/challenges/Find%20The%20Easy%20Pass>
- <https://github.com/dnSpy/dnSpy>
