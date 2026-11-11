---
challenge: FlagCasino
category: Reversing
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, prng, rand, ctypes]
---

# FlagCasino — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A 64-bit ELF asks for the flag **one character at a time**. For each character it calls `srand(c)` and compares `rand()` against an entry of the `check` array. Since the seed is the character itself, walking the 95 printable values, generating the first `rand()` for each seed and keeping the character whose value matches `check[i]` recovers the flag. Thirty comparisons, thirty characters.

## Brief and surface

- Reversing, Very Easy; Business CTF 2024 challenge.
- A single binary, `casino`, with no source code.
- The story is an abandoned casino whose robots take bets: the "bet" is the flag.

## Recon

```bash
file casino
./casino
```

`file` reports a 64-bit LSB x86-64 ELF, dynamically linked and **not stripped**. Running it prints an ASCII banner and prompts with `> `. Any wrong character answers `[ * INCORRECT * ]` and exits with the evacuation warning.

`strings` does not show the flag: the binary does not store it, it **validates** it.

## Source analysis

In Ghidra, `main` is short:

```c
i = 0;
while (true) {
    if (29 < i) { puts("[ ** HOUSE BALANCE $0 - PLEASE COME BACK LATER ** ]"); return 0; }
    printf("> ");
    if (__isoc99_scanf(" %c", &c) != 1) break;
    srand((int)c);
    if (rand() != check[i]) {
        puts("[ * INCORRECT * ]");
        exit(-2);
    }
    puts("[ * CORRECT *]");
    i++;
}
```

- `check` is an `int[30]` in `.data`, at `0x104080`, holding 30 32-bit values.
- The loop runs `i = 0..29`: the flag is **30 characters** long.
- `srand(c)` seeds the PRNG with the input character and `rand()` is the first output for that seed.

## The bug

The check uses neither a hash nor a key: it uses a PRNG **seeded with the secret**. `rand()` is deterministic for a given seed, so the value expected at `check[i]` identifies the seed that produces it. The seed space is the printable characters (95 options), not the whole flag.

## Local reproduction

```bash
chmod +x casino
./casino
# type characters by hand to see the verdict per position
```

GDB works too: break on the comparison and read `check[i]` and the computed `rand()` on every iteration.

## Exploitation

With `pwntools` the array is read straight from the ELF, and `ctypes` reproduces the system libc `rand()`:

```python
import ctypes
from pwn import ELF

libc = ctypes.CDLL("libc.so.6")
mapping = {}
for c in range(0x20, 0x7f):
    libc.srand(c)
    mapping[libc.rand()] = chr(c)

e = ELF("./casino", checksec=False)
flag = "".join(mapping[e.u32(e.sym["check"] + i * 4)] for i in range(30))
print(flag)
```

A C alternative without pwntools: copy the array from Ghidra into `int check[30]` and run the same `srand(c); rand()` double loop for `c` in `0x20..0x7e`.

Important: glibc and the Windows CRT **do not produce the same sequence** for the same seed. The binary is an ELF, so reproduction must use glibc.

## Evidence

- `casino`, a 64-bit ELF, not stripped.
- A 30-entry `check` array at `0x104080`.
- `[ * CORRECT *]` printed 30 times for the right sequence; the flag is kept in `private/`.

## Lessons learned

- **Seed equals data**: seeding a PRNG with the secret turns each comparison into a 95-seed brute force, not a flag brute force.
- **Copying the array wrong**: reading `check` as bytes instead of `uint32` shifts the values and nothing matches.
- **Testing on another OS**: `rand()` sequences differ between glibc and the Windows CRT.

## Mitigations and detection

- Never validate a secret with a PRNG seeded by that secret: it is a 95-entry lookup table.
- For real comparisons use a salted KDF (Argon2, scrypt) and a constant-time compare.
- Detection: binaries calling `srand` with user input and comparing `rand()` against a constant table; YARA can hunt the `srand`/`rand`/32-bit array pattern.

## References

- <https://github.com/hackthebox/business-ctf-2024/tree/main/reversing/%5BVery%20Easy%5D%20FlagCasino>
- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/flagcasino/>
- <https://man7.org/linux/man-pages/man3/rand.3.html>
