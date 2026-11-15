---
topic: PHP — integer overflow in native extensions
tags: [linux, php, extension, integer-overflow, gdb]
---

# PHP — integer overflow in native extensions

**English** | [🌐 Español](php-extension-integer-overflow.md)

## Concept

A PHP extension written in C may compute indexes or sizes with unchecked integers. A large value overflows and produces a negative index or a smaller size, allowing stack or heap overwrite. If the PHP process runs as root or with privileges, execution is direct.

## When it applies

- The application loads a custom native extension.
- The extension processes a user-controlled integer.
- A local copy of the binary is available for debugging.

## Procedure

1. Identify the extension and exposed function.
2. Reproduce the calculation with boundary values.
3. Debug with GDB and locate the overwritten variable.
4. Build the payload and control the flow.

## Commands

```bash
php -m
php -i | grep extension_dir
gdb -q -p <PID>
# Value that overflows the index
curl "http://<HOST>/index.php?n=9223372036854775807"
checksec --file=$(which php)
```

## Variants

- Overflow an `int` used as a `memcpy` size.
- Use a negative index to write before the buffer.
- Combine it with an address leak from PHP itself.

## Limitations

- The extension may validate the range.
- The binary may use ASLR/PIE.
- The production environment may differ from local.

## Mitigation

- Validate integers and add bounds checks.
- Build with `-fstack-protector` and `-D_FORTIFY_SOURCE=2`.
- Run PHP as an unprivileged user.

## Detection

- Extreme values in numeric parameters.
- PHP crashes with segfaults.
- Outdated native extensions.

## References

- [0xdf — Ouija](https://0xdf.gitlab.io/2024/05/18/htb-ouija.html)
- [PHP — Writing extensions](https://www.php.net/manual/en/internals2.php)
- [CWE-190 — Integer Overflow](https://cwe.mitre.org/data/definitions/190.html)
