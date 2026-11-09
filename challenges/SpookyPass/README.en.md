---
challenge: SpookyPass
category: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, strings, static-analysis]
---

# SpookyPass — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A 64-bit ELF asks for a password and prints the flag when it is correct. The password sits **in clear text** in the binary: `strings` finds it without a disassembler. The flag is also present as UTF-32 text (one character every four bytes).

## Evidence

- `pass`, an ELF executable.

## Method

1. **Triage**:

```bash
file pass; chmod +x pass
strings -n 6 pass | less
```

2. **Password**: among the strings appears `s3cr3t_p455_f0r_gh05t5_4nd_gh0ul5`. Running it validates and prints the flag.

3. **Flag without executing**: on binaries with UTF-32 strings, `strings -e l` extracts 32-bit text:

```bash
strings -e l pass | grep -i htb
```

4. **Static alternative**: open in Ghidra/IDA and read the `strcmp` in `main`; both strings sit together.

## Pitfalls

- **UTF-32 strings**: plain `strings` does not show them as continuous text; use `-e l` or inspect the hex dump.
- **Running it outside the VM**: unnecessary; static analysis is enough.
- **Pipes truncating output**: the flag may split on screen; redirect to a file.

## Lessons

- An unobfuscated binary leaks secrets through its strings.
- A debugger is not always needed: `strings` solves plenty of challenges.
- Try encoding variants (ASCII, UTF-16, UTF-32) when text looks like garbage.
