---
challenge: Bat Computer
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, binary, patch, serial, ghidra]
---

# Bat Computer — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

A binary asks for a password and compares characters through a simple transformation. Static analysis with `strings` and a disassembler reveals the logic; rebuild the valid input or patch the comparison to obtain the flag.

## Prompt and surface

- Reversing, Easy, retired.
- An executable and a challenge description are provided.
- The goal is to find the correct input.

```bash
file bat-computer
strings -n 6 bat-computer | head
```

## Reconnaissance

```bash
chmod +x bat-computer
./bat-computer
ltrace ./bat-computer
```

- The binary is a native executable.
- It asks for a string and prints success or failure.
- `strings` reveals messages and possible constants.

## Analysis

Open it in Ghidra/objdump and locate `main`. The comparison walks the input, applies XOR or addition and compares against a table. Document the constants and invert the transformation.

```c
for (i = 0; i < len; i++)
    if ((input[i] ^ key[i]) != target[i]) return 1;
```

## Exploitation

Rebuild the input with a script or patch the conditional jump to accept any string. The flag appears when running the binary with the valid input; do not publish it.

```python
print(bytes(a ^ b for a, b in zip(target, key)))
```

## Evidence

- Comparison logic identified.
- Rebuilt input or applied patch.
- Success message and flag.

## Lessons

- `strings` and `ltrace` speed up triage.
- A simple transformation is invertible with a script.
- Patching a jump helps validate the path.
- Documenting constants and offsets makes the analysis repeatable.

## Mitigations and detection

- Do not protect secrets with local checks.
- Obfuscation is not cryptography.
- Sign binaries and verify integrity.
- Review executables containing flag or key strings.
- References: Ghidra, x86 reversing.

## References

- <https://www.hackthebox.com/challenges/Bat%20Computer>
- <https://ghidra-sre.org/>
- <https://en.wikipedia.org/wiki/Disassembler>
- <https://attack.mitre.org/techniques/T1027/>
