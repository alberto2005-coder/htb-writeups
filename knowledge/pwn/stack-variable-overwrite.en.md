---
topic: Stack variable overwrite
tags: [pwn, stack, buffer-overflow, gets, variable-overwrite, pwntools]
---

# Stack variable overwrite

**English** | [🇪🇸 Español](stack-variable-overwrite.md)

## Concept

A buffer overflow does not always aim at the return address. If a local variable controls a security branch and sits next to the buffer, writing more bytes than reserved overwrites it and activates privileged code.

## When it applies

- `gets`, `strcpy`, `sprintf` or `read` with the wrong length.
- Local variables such as `is_admin`, `check` or `authenticated`.
- Dead code that reads the flag or calls a function.
- No canary and no length checks.

## Procedure

1. Disassemble `main` and map the stack frame.
2. Measure the offset between buffer and target variable.
3. Check variable order and size.
4. Build the payload with padding and the desired value.
5. Send it and verify the branch.

```python
from pwn import *
payload = b"A" * 60 + p64(0x1337bab3)
p = process("./challenge")
p.sendline(payload)
print(p.recvall())
```

## Variants

- 4-byte variable aligned after the buffer.
- Overwriting a local function pointer.
- Overwriting an index or a size.
- Overflow that also hits the canary and return address.

## Limitations

- The compiler may reorder or align variables.
- A canary between buffer and target detects corruption.
- PIE does not matter when only a value changes.
- Input may terminate on a null byte.

## Mitigation and detection

- Use bounded functions and check length.
- Build with canary, NX and PIE.
- Never use local variables for security decisions.
- Alert on crashes and abnormally long input.

## References

- <https://man7.org/linux/man-pages/man3/gets.3.html>
- <https://cwe.mitre.org/data/definitions/121.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://github.com/Gallopsled/pwntools>
