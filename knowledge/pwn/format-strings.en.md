---
title: "Format strings: reading and writing with printf"
tags: [pwn, format-string, printf, cwe-134, x86-64]
---

# Format strings: reading and writing with `printf`

**English** | [🇪🇸 Español](format-strings.md)

## 1. When to look here

The program passes user input as the first argument of `printf`, `fprintf`, `sprintf` or `snprintf`. No overflow needed: the format reads the stack and writes to addresses.

```c
printf(user_input);        // vulnerable
printf("%s", user_input);  // correct
```

## 2. What each specifier does

| Specifier | Effect |
|---|---|
| `%lx` | reads one argument (8 bytes) and prints it in hex |
| `%s` | treats the argument as a string pointer |
| `%n` | writes the number of printed characters to the pointer |
| `%hn` | same, as `unsigned short` (2 bytes) |
| `%hhn` | same, as one byte |

With too few arguments, `printf` takes values from the stack and saved registers. That is why `%lx.%lx.%lx` walks the contents.

## 3. Positional arguments

`%6$lx` reads the sixth argument without consuming the previous ones; `%7$hn` writes to the seventh. The index depends on the architecture and build: on x86-64 the first ones go in registers (`rsi`, `rdx`, `rcx`, `r8`, `r9`) and the rest on the stack, so it cannot be assumed.

Enumerating is the reliable way:

```text
%lx.%lx.%lx.%lx.%lx.%lx.%lx.%lx
```

When the known value appears (for example `deadbeef`), that is its index; the address usually comes right after.

## 4. Writing with `%n`

`%n` writes the accumulated count, not an arbitrary value. To write `0x1337`:

```text
%4919c%7$hn
```

- `%4919c` prints 4919 characters (0x1337).
- `%7$hn` writes those 2 bytes to the address of argument 7.

Larger values are split into two writes (`%hn` low and high) or done byte by byte with `%hhn`. Order matters: the counter only grows, so write the smaller value first and pad the rest.

## 5. When the address is not on the stack

If the pointer does not show up, place it in the format itself (8-byte aligned) and reference it with a computed index. On x86-64 the format arrives in `rdi`, so the first payload bytes can be the address; adjust the index until `%N$hn` points at it.

## 6. Limits and mistakes

- **`%n` blocked by glibc**: with `_FORTIFY_SOURCE` and formats in read-only memory it may abort; in a CTF, test locally.
- **Wrong index**: the payload writes to a garbage address and the process dies.
- **Format too long**: the `read` limits bytes; if address and padding do not fit, use several steps.
- **`%s` with an invalid pointer**: segfault; useful to probe indexes, not to leak.
- **PIE and ASLR**: if the target is in the binary or on the stack, leak its address first with `%lx` or `%s`.

## 7. Detection and mitigation

- Never pass input as a format; use `printf("%s", buf)` or `fputs`.
- Build with `-Wformat -Wformat-security` and `_FORTIFY_SOURCE=2`.
- Detection: requests with `%n`, `%hn`, `%s` or `%lx` chains; SIGSEGV crashes after input containing `%`.
- CWE-134 (uncontrolled format string); MITRE T1190.

References: `man 3 printf`, CWE-134 and the pwntools notes on `fmtstr_payload`.
