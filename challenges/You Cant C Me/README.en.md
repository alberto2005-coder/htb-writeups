---
challenge: You Cant C Me
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, ltrace, strcmp]
---

# You Cant C Me — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real flag.

## TL;DR

The `auth` binary asks for a key and compares it with `strcmp`. It is stripped, but `ltrace` shows the call and its second argument: the correct key. Entering it prints the flag.

## Brief and surface

- Reversing, Very Easy, retired.
- An ELF `auth` is provided.
- The program only asks for a key on stdin.

```bash
file auth
checksec --file=auth
```

## Recon

```bash
./auth
# Welcome!
# Insert key:
```

Any input gets a negative response. `strings` does not reveal the comparison because the binary is stripped, but `ltrace` shows libc calls.

## Source analysis

```bash
ltrace ./auth
```

The trace includes:

```text
strcmp("<KEY>", "<INPUT>")
```

The first argument is the expected key; the second is user input. No decompilation is needed: the comparison happens in libc and `ltrace` intercepts it.

## The bug

The check runs client-side with `strcmp`, and the key is in memory. Anyone can observe it with a debugger or `ltrace`. There is no obfuscation or hash comparison.

## Local reproduction

```bash
ltrace ./auth
# Enter any string
```

`gdb` also works:

```bash
gdb -q ./auth
break strcmp
run
```

At the breakpoint, `$rdi` and `$rsi` hold both strings.

## Exploitation

Run the binary with the observed key:

```bash
printf '<KEY>\n' | ./auth
```

The correct output contains the flag. Redact it in evidence.

## Evidence

- `file` and `checksec`.
- `ltrace` output with the `strcmp` call.
- Run with the key and redacted flag.

## Lessons learned

- `ltrace` is enough for libc comparisons.
- A stripped binary does not hide dynamic function calls.
- A `gdb` breakpoint on `strcmp` confirms the key.
- A cleartext key in memory is trivial to extract.

## Mitigations and detection

- Never store secrets in client binaries.
- Compare salted hashes and verify server-side.
- Obfuscation is not a substitute for secure design.
- Detection: limited in a CTF; in production, review secret exposure.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/you-cant-c-me/>
- <https://sourceware.org/gdb/current/onlinedocs/gdb/>
- <https://man7.org/linux/man-pages/man1/ltrace.1.html>
