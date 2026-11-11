---
challenge: Oldbridge
category: Challenge
type: pwn
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [pwn, canary, pie, stack-pivot, ret2libc, xor, brute-force]
---

# Oldbridge — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired based on public writeups; not verified with an HTB session.
> No flags or real instance addresses.

## TL;DR

A service XORs input with `0xd` and compares the username against `il{dih` ("davide"). `check_username()` copies 1056 bytes into a 1032-byte buffer: canary, saved rbp and return address are reachable, but there is no room for a ROP chain. Because the server `fork()`s, the canary and PIE base can be recovered byte by byte. With them, a **stack pivot** (`leave; ret`) moves the stack into the buffer and a ret2libc runs `write`, `dup2` and `system`.

## Brief and surface

- **Pwn** category, **Medium** difficulty, x86-64 ELF and a remote instance.
- The binary asks for a username and answers `Username found!` on a match.
- Input is XOR-encoded before comparison: send the bytes already encoded.

```bash
file oldbridge
checksec --file=oldbridge
```

```text
RELRO:    Partial RELRO
Stack:    Canary found
NX:       NX enabled
PIE:      PIE enabled
```

Almost every protection is on: canary, PIE and libc ASLR all need solving.

## Recon

```bash
./oldbridge 1234
nc 127.0.0.1 1234
```

```text
Username: davide
Username found!
```

The expected username is embedded as `il{dih`; XOR `0xd` reverses it:

```python
bytes(c ^ 0xD for c in b'il{dih')   # b'davide'
```

From there, the server `fork()`s per connection: the child inherits the parent's canary, PIE base and stack. That is what makes brute force viable.

## Source analysis

`check_username()` reserves `0x430` bytes and places the buffer at `rbp-0x410` (1032 bytes). Then:

```c
read(fd, rbp - 0x410, 0x420);   // 1056 bytes
...
if (strcmp(cifrado, "il{dih") == 0) write(fd, "Username found!\n", ...);
```

The `0x420` (1056) read covers exactly:

```text
rbp-0x410  [ buffer, 1032 bytes ]
rbp+0x000  [ canary, 8 bytes ]
rbp+0x008  [ saved rbp, 8 bytes ]
rbp+0x010  [ return address, 8 bytes ]
```

1032 + 8 + 8 + 8 = 1056. Not a single byte is left for a ROP chain: only **one** return address can be written. Hence the pivot.

## The bug

### Canary and PIE by brute force

The parent does not die when a child fails. Sending 1032 filler bytes and trying the next byte (0–255) yields `Username found!` only when the canary byte is right. Repeat for the 8 canary bytes, the 8 `saved rbp` bytes and the 6–7 return bytes.

- The canary ends in `00`; the first byte is known and the rest are tested.
- `check_username`'s return ends in `0xcf` (`main+566`), shrinking the search space.
- The PIE base is `return - 0xecf`; from there, gadgets and PLT have fixed offsets.

Input is XOR-encoded with `0xd`, so every tested byte is sent as `value ^ 0xd`. The canary's `00` travels as `0x0d`.

### Stack pivot

With no room for ROP, the `leave; ret` gadget is used:

```asm
leave      ; mov rsp, rbp ; pop rbp
ret
```

If `saved rbp` points into the buffer, `leave` moves `rsp` there, `pop rbp` consumes the first 8 bytes and `ret` jumps into the chain written in the filler. The distance between `saved rbp` and the buffer start is build-dependent: `0x480` in one writeup, `0x478` in the other.

### Build offsets

| Item | Offset from base |
|---|---:|
| `check_username` return | `0xecf` |
| `leave; ret` | `0xb6d` or `0xc5c` per build |
| `pop rdi; ret` | `0xf73` |
| `pop rsi; pop r15; ret` | `0xf71` |
| `pop rdx; ret` | `0xb53` |
| `write@plt` | `0x910` |
| `write@got` | `0x202020` |

The two writeups use different binaries: never copy offsets without checking `objdump` and `ROPgadget`.

## Local reproduction

```bash
./oldbridge 1234
python3 solve.py 127.0.0.1:1234
```

To verify the frame:

```gdb
break *check_username+90
run
# after the read
x/6gx $rbp-0x410
```

The canary sits at `rbp`, the saved rbp at `rbp+8` and the return at `rbp+16`.

## Exploitation

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = '<IP>', '<PORT>'
KEY = 0xD

def enc(data):
    return bytes(b ^ KEY for b in data)

# 1. Brute force canary, saved rbp and return (forking server)
# 2. base = ret - 0xecf
# 3. pivot: saved rbp = buffer_addr - 0x480
# 4. ROP: write(4, write@got, 8); return to check_username
# 5. libc.rip with the low 3 nibbles; dup2(4, 0/1/2); system('/bin/sh')
```

Things that must be right:

- The whole payload is XOR-encoded with `0xd`; one plain byte breaks the canary or the address.
- The socket fd is usually 4; if not, try 3, 5 and 6.
- The first chain only leaks `write`; the second returns to `check_username` with the libc base known.
- `dup2` redirects the socket to stdin/stdout/stderr before `system`.
- Confirm libc offsets with `libc.rip` from the low 12 bits of the leak.

## Evidence

- `checksec` with canary, NX and PIE.
- Canary and return recovered byte by byte using `Username found!` as an oracle.
- PIE base computed and `write` leaked through the ROP chain.
- Local shell with a test flag, never the real one.

## Lessons learned

- A `fork()` without `exec` makes the canary guessable: the child inherits the secret and the parent stays alive.
- XOR on input is not cryptographic protection: the same byte reverses it.
- When the read reaches exactly the return address, ROP needs a stack move first; `leave; ret` is the minimal pivot.
- The saved rbp is not filler: it decides where the chain continues.
- Offsets change between builds; two writeups of the same challenge can differ in `leave; ret` and buffer distance.

## Mitigations and detection

- `fork()` + `exec()` per connection, or re-key the canary, so it is not inherited.
- Build with `-fstack-protector-strong`, `-pie -fPIE` and `-D_FORTIFY_SOURCE=2`; the read must use `sizeof`.
- Never compare credentials with XOR or embedded strings; use a salted hash.
- Detection: many connections failing on the same byte and one answering differently; 1032–1056-byte requests with non-printable bytes; repeated child crashes.
- References: CWE-121, CWE-798 (hardcoded credentials), MITRE T1190.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/old-bridge/>
- <https://shaked.delarea.cloud/posts/blog-2>
- <https://cwe.mitre.org/data/definitions/121.html>
- <https://libc.rip/>
- <https://docs.pwntools.com/en/stable/rop/rop.html>
