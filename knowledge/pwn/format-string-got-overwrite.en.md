---
topic: Format string y sobrescritura de GOT
tags: [pwn, format-string, got, libc, pwntools]
---

# Format String and GOT Overwrite

**English** | [🇪🇸 Español](format-string-got-overwrite.md)

## Concept

`printf(buf)` interprets input as a format. `%p` leaks the stack, `%s` reads pointers and `%n` writes to an address. If the GOT is writable, a function can be redirected to `system`.

## When it applies

- Binaries printing input without a fixed format.
- `printf`, `fprintf` or `syslog` with a controlled buffer.
- Partial or no RELRO.

## Procedure

1. Confirm with `AAAA.%p.%p`.
2. Find the offset with `%N$p`.
3. Leak a libc or stack address.
4. Compute `system` and `/bin/sh`.
5. Write with `%n` to the GOT and call the function.

```python
from pwn import *
payload = fmtstr_payload(offset, {elf.got['printf']: libc.symbols['system']})
```

## Variants

- `%hhn` for one-byte writes.
- Overwrite `exit` or `free`.
- Use `%s` to read memory.

## Limitations

- Full RELRO protects the GOT.
- ASLR requires a prior leak.
- The offset changes with architecture and stack layout.

## Mitigation

- `printf("%s", buf)` and constant formats.
- Build with `-Wformat-security` and full RELRO.
- ASLR/PIE and code review.

## Detection

- Strings with many `%p`, `%n` or `%s`.
- Crashes in `printf`.
- Anomalous GOT writes.

## References

- <https://owasp.org/www-community/attacks/Format_string_attack>
- <https://docs.pwntools.com/en/stable/fmtstr.html>
- <https://attack.mitre.org/techniques/T1203/>
