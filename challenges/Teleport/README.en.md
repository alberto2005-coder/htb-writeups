---
challenge: Teleport
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, ghidra, setjmp, password]
---

# Teleport — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real key or flag.

## TL;DR

The `teleport` binary takes the password as an argument and validates it with dozens of functions using `setjmp`/`longjmp`. Each function compares a byte at a different offset, in non-sequential order. Exporting Ghidra's decompilation reveals the comparisons; sort them by offset to rebuild the password.

## Brief and surface

- Reversing, Easy, retired.
- An ELF `teleport` is provided.
- Usage: `./teleport <password>`.

```bash
file teleport
checksec --file=teleport
```

## Recon

```bash
./teleport
# Missing password
./teleport test
# Something's wrong...
ltrace ./teleport test
```

`ltrace` shows `strncpy`, multiple `_setjmp` calls and byte comparisons. The binary is not obfuscated, but the logic is spread out.

## Source analysis

In Ghidra, `main` copies the argument to a global buffer and calls validation functions. Each function:

1. Calls `_setjmp`.
2. Compares a buffer byte with a character.
3. On failure, calls `longjmp(..., 101)`.

Offsets are not sequential. Export the pseudocode and extract lines such as:

```c
if (DAT_00303296 != 'p') longjmp(...);
if (DAT_003032a5 != 'n') longjmp(...);
if (DAT_00303281 != 'T') longjmp(...);
```

## The bug

Validation is fragmented to hinder reading, but each comparison reveals a byte and its position. There is no hash or transformation: the password is embedded as immediate comparisons.

## Local reproduction

Export the decompilation and process it with `grep`/`awk` to sort by offset:

```bash
grep -oE "DAT_[0-9a-f]+ != '[^']'" decompiled.c | sort -u
```

Convert the offset to a buffer index and rebuild the string. A Ghidra script can also walk `CMP` instructions and their immediates.

## Exploitation

```bash
./teleport '<PASSWORD>'
```

The correct output contains the flag. Verify and redact it.

## Evidence

- `checksec` and `ltrace`.
- Decompiled excerpt with offsets and characters redacted.
- Run with the password and redacted flag.

## Lessons learned

- `setjmp`/`longjmp` obfuscates control flow, not data.
- Immediate comparisons leak the password.
- Ghidra plus scripting beats manual flow following.
- Offset order is the key to reconstruction.

## Mitigations and detection

- Do not validate secrets client-side with byte-by-byte comparisons.
- Use salted hashes and server-side verification.
- Control-flow obfuscation is not secure design.
- Detection: in CTFs, review `setjmp`; in production, avoid embedded secrets.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/teleport/>
- <https://ghidra-sre.org/>
- <https://en.wikipedia.org/wiki/Setjmp.h>
