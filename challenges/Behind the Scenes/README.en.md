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

A 64-bit ELF with **no debug info but symbols intact** (`main` is still there) asking for a 12-character password. The binary installs a `SIGILL` handler and executes **`UD2`** (`0f 0b`): the invalid-opcode exception fires, the handler resumes past it, and decompilers lose the thread. Ghidra shows an almost empty `main`; with **GDB** (or by marking the byte after each `UD2` as code) the four `strcmp` calls and their literals appear.

## Evidence

- `behindthescenes`, a 64-bit ELF: no debug info, symbols intact.

## Method

1. **Check the hint**: running it asks for `./challenge <password>`; `strings` reveals nothing.

2. **GDB instead of the decompiler**:

```bash
gdb -q ./behindthescenes
(gdb) disas main
```

`UD2` is an "invalid" instruction that breaks static analysis; the real flow is visible in assembly.

3. **Four `strcmp` calls**: each compares a 3-4 character chunk. Break on each call and read the second argument (`x/s $rsi`), or inspect the hexdump next to the code.

4. **Rebuild**: the password is the concatenation of the fragments (`Itz` + `_0n` + `Ly_` + `UD2`).

```bash
./behindthescenes Itz_0nLy_UD2
```

5. The flag is `HTB{<password>}`.

## Pitfalls

- **`UD2` and Ghidra**: garbage output does not make it unsolvable; switch to GDB.
- **`SIGILL`, not `NOP`**: the binary does not die at `UD2`; the handler steps over it. Patching to `NOP` is a convenience, not a requirement.
- **Length**: the program demands 12 bytes; count the fragments before trying.

## Why it works

`main` calls `sigaction(SIGILL, ...)` and then `ud2`. The CPU raises the invalid-opcode exception, the installed handler advances `RIP` and returns, so execution continues on the next instruction. Static tools stop at the first `UD2`, which is the whole trick: the code is still there.

## Mitigation

There is no vulnerability here: the challenge shows that **obfuscation does not protect a secret**. If the password is checked client-side it can be extracted; `UD2` only annoys the tool, not the analyst.

- Practical rule: no secret embedded in a distributed binary; if unavoidable, derive it per user and verify server-side.

## Lessons

- "Anti-decompilation" is obfuscation: assembly still tells the truth.
- Comparing split strings is a way to hide a secret in code.
- Knowing when to abandon a tool matters as much as using it.
