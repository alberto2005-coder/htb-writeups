---
topic: SUID — staged buffer overflow
tags: [linux, suid, buffer-overflow, canary, aslr]
---

# SUID — staged buffer overflow

**English** | [🌐 Español](suid-buffer-overflow.md)

## Concept

A SUID binary reading more data than its buffer allows can overwrite the stack. With a canary and ASLR, stages are chained: leak addresses, compute the canary and use a second overflow to control the return. The goal is a shell with root effective UID.

## When it applies

- A SUID binary accepts user input.
- `checksec` shows NX and a canary, but no PIE or a leak exists.
- The binary can be debugged locally with the same version.

## Procedure

1. Copy the binary and run `checksec`.
2. Crash it and measure the offset with `patternget`.
3. Leak the canary, libc base or PIE in a first stage.
4. Build the ROP or ret2libc and run the second stage.

## Commands

```bash
find / -perm -4000 -type f 2>/dev/null
checksec --file=/usr/local/bin/<BIN>
gdb -q /usr/local/bin/<BIN>
patternget 100
python3 exploit.py
id
```

## Variants

- Ret2libc when NX is enabled.
- ROP with `pop rdi; ret` for `system`.
- Abuse a `gets` or `read` with the wrong size.

## Limitations

- The binary may use PIE and full RELRO.
- The remote version must match the local one.
- The environment may restrict `ptrace` or `execve`.

## Mitigation

- Build with `-fstack-protector-strong`, PIE and full RELRO.
- Remove unnecessary SUID bits.
- Validate lengths and use safe functions.

## Detection

- Crashes of SUID binaries with long input.
- Core dumps from privileged processes.
- Shells spawned by a SUID binary.

## References

- [0xdf — Calamity](https://0xdf.gitlab.io/2020/08/27/htb-calamity.html)
- [GDB — Debugging](https://sourceware.org/gdb/documentation/)
- [CWE-121 — Stack-based Buffer Overflow](https://cwe.mitre.org/data/definitions/121.html)
