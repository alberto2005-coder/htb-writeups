---
challenge: Nightmare
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, format-string, got-overwrite, libc, pwntools]
---

# Nightmare — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

The binary prints input with `printf` and no fixed format. A format string leaks stack and libc addresses; with the `system` address, a GOT entry is overwritten and `/bin/sh` runs on the next call.

## Prompt and surface

- Pwn, Easy, retired.
- An ELF and a remote service are provided.
- The goal is a shell and the flag.

```bash
file nightmare
checksec --file=nightmare
```

## Reconnaissance

```bash
./nightmare
python3 -c 'print("AAAA.%p.%p.%p")' | ./nightmare
```

- 64-bit binary, PIE and NX.
- `printf(buf)` with user input.
- A later call reaches a libc function.

## Analysis

The format string reads positional arguments (`%7$p`) and writes with `%n`. Find the stack offset and leak a return or GOT address to calculate the libc base.

```python
from pwn import *
elf = ELF('./nightmare')
libc = ELF('./libc.so.6')
```

## Exploitation

Compute `system` and `/bin/sh`, write `system` into the GOT entry for `printf` or `exit` with `fmtstr_payload`, and send `/bin/sh` as the next input.

```python
payload = fmtstr_payload(offset, {elf.got['printf']: libc.symbols['system']})
```

## Evidence

- Leaked libc address.
- GOT overwritten with `system`.
- Shell and flag read without publishing it.

## Lessons

- `printf(user_input)` is a format-string vulnerability.
- A libc leak defeats ASLR.
- GOT remains a target without full RELRO.
- `pwntools` automates payload calculation.

## Mitigations and detection

- Use `printf("%s", buf)` and constant formats.
- Build with `-Wformat-security` and full RELRO.
- Enable ASLR and PIE; do not rely on NX alone.
- Monitor crashes and strings with many `%p`/`%n`.
- References: OWASP Format String, pwntools.

## References

- <https://www.hackthebox.com/challenges/Nightmare>
- <https://owasp.org/www-community/attacks/Format_string_attack>
- <https://docs.pwntools.com/en/stable/fmtstr.html>
- <https://attack.mitre.org/techniques/T1203/>
