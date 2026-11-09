---
challenge: Behind the Scenes
category: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, gdb, ud2, anti-decompilation]
---

# Behind the Scenes — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A `stripped` ELF asking for a 12-character password. The author inserted **`UD2`** instructions so decompilers lose their way: Ghidra shows an almost empty `main`. The answer is to drop to **GDB**, inspect the four `strncmp` calls and read the compared literals.

## Evidence

- `behindthescenes`, a `stripped` ELF executable.

## Method

1. **Check the hint**: running it asks for `./challenge <password>`; `strings` reveals nothing.

2. **GDB instead of the decompiler**:

```bash
gdb -q ./behindthescenes
(gdb) disas main
```

`UD2` is an "invalid" instruction that breaks static analysis; the real flow is visible in assembly.

3. **Four `strncmp` calls**: each compares a 3-4 character chunk. Break on each call and read the second argument (`x/s $rsi`), or inspect the hexdump next to the code.

4. **Rebuild**: the password is the concatenation of the fragments (`Itz` + `_0n` + `Ly_` + `UD2`).

```bash
./behindthescenes Itz_0nLy_UD2
```

5. The flag is `HTB{<password>}`.

## Pitfalls

- **`UD2` and Ghidra**: garbage output does not make it unsolvable; switch to GDB.
- **Patching**: turning `UD2` into `NOP` lets you follow the flow, but it is not required.
- **Length**: the program demands 12 bytes; count the fragments before trying.

## Lessons

- "Anti-decompilation" is obfuscation: assembly still tells the truth.
- Comparing split strings is a way to hide a secret in code.
- Knowing when to abandon a tool matters as much as using it.
