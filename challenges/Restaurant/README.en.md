---
challenge: Restaurant
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, ret2libc, buffer-overflow, rop, elf]
---

# Restaurant — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The 64-bit binary has a stack overflow with no canary. Leak `puts@got` with a two-stage ROP, compute the libc base and call `system("/bin/sh")`. The libc ships with the challenge.

## Brief and surface

- Pwn, Easy, retired.
- `restaurant` and `libc.so.6` are provided.
- Remote TCP service.

```bash
file restaurant
checksec --file=restaurant
# NX, no PIE, no canary, full RELRO
```

## Recon

```bash
./restaurant
# menu / input prompt
```

The program reads more bytes than the stack buffer holds. Compute the return-address offset with `cyclic`/`pwndbg`:

```bash
gdb -q ./restaurant
cyclic 200
```

## Analysis

Without PIE, binary addresses are fixed. Stage one calls `puts(puts@got)` and returns to `main` to repeat the overflow. Stage two uses the leak to compute the libc base and run `system("/bin/sh")`.

```python
rop = ROP(elf)
rop.call(elf.plt['puts'], [elf.got['puts']])
rop.call(elf.symbols['main'])
```

## The bug

The program does not limit input length and copies into a stack buffer. With no canary and no PIE, a basic ROP is enough; the provided libc gives `system` and `/bin/sh` offsets.

## Local reproduction

1. Compute the offset.
2. Build the leak ROP.
3. Receive the `puts` address.
4. Compute the libc base.
5. Send the second ROP with `system("/bin/sh")`.

```python
libc.address = leak - libc.symbols['puts']
```

## Evidence

- `checksec` and offset.
- `puts` leak and computed libc base.
- Remote shell and redacted flag.

## Lessons learned

- Without PIE, binary ROP is direct.
- A GOT leak defeats libc ASLR.
- Returning to `main` enables a second stage.
- Use the challenge libc for offsets.

## Mitigation and detection

- Compile with PIE, canary and `FORTIFY_SOURCE`.
- Validate input lengths.
- Use bounded `read`.
- In CTFs, document the libc version.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/restaurant/>
- <https://docs.pwntools.com/>
- <https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/ret2libc/>
