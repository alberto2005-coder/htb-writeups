---
title: Partial overwrite of return addresses
tags: [pwn, buffer-overflow, partial-overwrite, aslr, pie, x86-64]
---

# Partial overwrite of return addresses

**English** | [🇪🇸 Español](partial-overwrite.md)

## 1. When to look here

An overflow lets you write fewer bytes than an address needs, or the program reads just one byte too many. If the binary has no PIE, the return address is already known and changing its low byte jumps to another branch of the same binary.

## 2. Why it works

Addresses in a non-PIE ELF are fixed (`0x400000` + offset). The low byte of the return address points to the instruction after the call; changing it can enter another instruction in the same block or a nearby branch.

```text
original return: 0x0000000000400ba0
low byte:                        ^^
new target:      0x0000000000400b01
```

The six high bytes do not need writing and ASLR does not need leaking: they do not change.

## 3. How many bytes can change

- **1 byte**: reaches targets within the next 256 bytes after the original return, inside the same page.
- **2 bytes**: covers 64 KB; useful to jump to another function if the page stays the same.
- **3 bytes or more**: part of the address is overwritten and must be known.

The `read` sets the limit: if the buffer is 40 bytes from the return and 57 are read, only one byte fits.

## 4. Computing the offset

```bash
python3 -c "from pwn import *; print(cyclic(100))"
```

Send the pattern, inspect `$rsp` at the crash and find the displacement:

```gdb
pattern search $rsp
```

There may be locals and the saved RBP between buffer and return; never assume the offset equals the buffer size.

## 5. Choosing the target

Disassemble the function and find the branch you want:

```bash
objdump -d -M intel binary | sed -n '/<function>:/,/^$/p'
```

Look for an instruction whose address shares the high bytes with the return and differs only in the low byte. In a CTF there is usually a branch that prints the flag or calls `system` a few bytes away.

## 6. Limits

- **PIE**: addresses change per run; leak the base (or use a 12-bit partial, which ASLR does not change).
- **Canary**: if it sits between buffer and return, leak it first.
- **ASLR and pages**: changing the low byte does not cross a page; targets in another page need more bytes.
- **Rebuilds**: any change moves the addresses and the computed byte stops working.

## 7. Detection and mitigation

- `-fstack-protector-strong` and `-pie -fPIE` turn the bug into one that needs a leak and a canary.
- Replace `read` with `fgets`/`read` using `sizeof`.
- Detection: crashes with `RIP` inside the binary after exact-length inputs; filler patterns followed by one control byte.
- CWE-121; MITRE T1190.

References: pwntools documentation (`cyclic`, `ELF`), CWE-121 and the Linux ASLR notes.
