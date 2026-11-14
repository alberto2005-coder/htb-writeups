---
topic: pwntools
tags: [pwn, pwntools, exploit, rop, shellcode, remote]
---

# pwntools

**English** | [🇪🇸 Español](pwntools.md)

## Concept

pwntools is a Python library for interacting with processes and services, building payloads and resolving addresses. `ELF`, `process`, `remote`, `cyclic`, `ROP` and `shellcraft` cover the usual pwn workflow.

## When it applies

- Challenges with a local or remote binary.
- Offset and address calculation.
- Building ROP chains.
- Interacting with prompts and menus.

## Procedure

1. Load the binary and check protections.
2. Calculate the offset with a cyclic pattern.
3. Choose the technique and build the payload.
4. Test locally and adjust.
5. Run against the remote service.

```python
from pwn import *
context.binary = elf = ELF('./challenge')
p = process('./challenge')
p.sendline(cyclic(128))
p.wait()
# p = remote('<HOST>', <PORT>)
```

## Variants

- `ROP` for gadget chains.
- `shellcraft` for shellcode.
- `fmtstr_payload` for format strings.
- `tube` for process interaction.

## Limitations

- Addresses change with ASLR and PIE.
- The remote libc may differ from the local one.
- The payload must respect the protocol.
- Some challenges require emulation.

## Mitigation and detection

- Apply ASLR, PIE, NX and canaries.
- Compile with `FORTIFY_SOURCE`.
- Monitor services receiving anomalous payloads.
- Test binaries before deployment.

## References

- <https://docs.pwntools.com/>
- <https://github.com/Gallopsled/pwntools>
- <https://ctf-wiki.org/pwn/linux/user-mode/environment/>
