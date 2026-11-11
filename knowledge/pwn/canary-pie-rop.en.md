---
title: "Canary, PIE and ROP: from leak to shell"
tags: [pwn, canary, pie, stack-pivot, ret2libc, aslr]
---

# Canary, PIE and ROP: from leak to shell

**English** | [🇪🇸 Español](canary-pie-rop.md)

## 1. When to look here

The binary has canary, PIE and NX, and the overflow reaches exactly the return address. Before writing a chain, three things must be solved: the canary, the binary base and the libc base. If there is no room for the chain, add a pivot.

## 2. The canary

It is an 8-byte random value between the buffer and the saved rbp. On x86-64 its low byte is `00`, which allows leaking it with string functions and cuts brute force to 7 bytes.

- **Direct leak**: `printf("%s")` or `write` over a buffer that contains it.
- **Brute force**: if the server `fork()`s without `exec`, every child shares the canary. Try byte by byte (256 options) and detect success because the child answers instead of dying.

```text
payload = filler + candidate
"User found" -> correct byte
child dies   -> next candidate
```

## 3. The PIE base

A function's return goes back to an address inside the binary. If leaked (same brute force or a `%p`), the base is `return - return_offset`. The low 12 bits of an address do not change with ASLR, so a known offset can be used as an anchor.

```python
base = ret_leak - 0xecf
gadget = base + 0xf73
```

## 4. Pivoting the stack

When the read ends exactly at the return address there is no room for more addresses. `leave; ret` does:

```asm
mov rsp, rbp
pop rbp
ret
```

If the saved rbp points into the buffer, the chain continues there. Compute the distance between saved rbp and the buffer start; it depends on the build and the locals.

Alternatives: `pop rsp`, `xchg rsp, rax`, or a function that copies the payload into a writable area.

## 5. A typical chain

1. `pop rdi; ret` → socket fd.
2. `pop rsi; pop r15; ret` → `write@got`.
3. `pop rdx; ret` → 8.
4. `write@plt` → leak the real `write` address.
5. Return to the vulnerable function to send the second chain.
6. With the libc base: `dup2(fd, 0/1/2)` and `system("/bin/sh")` or `execve`.

If the binary lacks gadgets, `__libc_csu_init` provides the classic ret2csu.

## 6. Encoded input

If the program XORs input (for example `0xd`), **the whole** payload is encoded, canary and addresses included. One plain byte breaks the frame and the process dies without explanation. The canary's `00` terminator is sent as `00 ^ key`.

## 7. Common mistakes

- **Wrong return offset**: the PIE base is shifted and every gadget fails.
- **Canary order**: test left to right, not backwards.
- **Fixed buffer distance**: it changes between builds; measure in GDB with `$rbp - $rsp` or a breakpoint after the read.
- **Socket fd**: not always 4; try several.
- **Different libc**: confirm `system`, `dup2` and `/bin/sh` offsets with the leak and libc.rip.
- **Misaligned stack**: `system` may fail on alignment; add one extra `ret`.

## 8. Detection and mitigation

- `fork()` + `exec()` per connection so the canary is not inherited.
- `-fstack-protector-strong`, `-pie -fPIE`, `-Wl,-z,relro,-z,now` and `read` with `sizeof`.
- Detection: many connections failing on the same byte and one answering differently; payloads exactly frame-sized; repeated crashes.
- CWE-121, CWE-798; MITRE T1190.

References: `man 3 read`, pwntools documentation (`ROP`, `ELF`), libc.rip and HackTricks stack pivoting notes.
