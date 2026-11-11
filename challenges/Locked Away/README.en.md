---
challenge: Locked Away
category: Misc
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, pyjail, python, blacklist, exec]
---

# Locked Away — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A textbook PyJail: the program checks a blacklist of strings and passes whatever survives to `exec()`. The list covers `open`, `flag`, `read`, `eval`, `exec`, `import`, brackets and quotes, but **not** `clear`. Calling `blacklist.clear()` empties it, and the next command can call `open_chest()` freely.

## Brief and surface

- Misc, Easy; Business CTF 2024.
- Ships `main.py` plus a remote instance over `nc`.
- The story is an entry test: the chest must be opened.

## Recon

```bash
nc <IP> <PORT>
```

The service prints an ASCII banner and the prompt `The chest lies waiting... `. Every command is checked against the blacklist; a hit answers `Invalid command!` and asks again. If the command raises, the program prints `You have been locked away...` and exits: no boolean extraction.

## Source analysis

```python
blacklist = [
    'import', 'os', 'sys', 'breakpoint',
    'flag', 'txt', 'read', 'eval', 'exec',
    'dir', 'print', 'subprocess', '[', ']',
    'echo', 'cat', '>', '<', '"', "'", 'open'
]

while True:
    command = input('The chest lies waiting... ')
    if any(b in command for b in blacklist):
        print('Invalid command!')
        continue
    try:
        exec(command)
    except Exception:
        print('You have been locked away...')
        exit(1337)
```

The check is a substring search, not a parser: any command without those exact terms gets through. `open_chest()` reads `flag.txt` and prints it, but its name contains `open` and `flag`, so it cannot be typed directly.

## The bug

The blacklist protects the function's name, not the object. `blacklist` is an ordinary global list and `exec` runs in the same namespace, so the list itself is a mutable object. Emptying it needs neither brackets nor quotes: the `clear()` method appears in no forbidden entry.

## Local reproduction

```bash
python3 main.py
```

Locally, creating a test `flag.txt` exercises the whole chain without touching the remote instance.

## Exploitation

```text
The chest lies waiting... blacklist.clear()
The chest lies waiting... open_chest()
```

1. `blacklist.clear()` passes the filter because it contains none of the listed substrings (no brackets, no quotes, no `open`).
2. The list is now empty, so `any(...)` is always false.
3. `open_chest()` can be called as-is and returns the file contents.

Equivalent variants: reassign with `blacklist.__init__()` or build the call through `getattr(__builtins__...)`, but `clear()` is the shortest and the one the author documents.

## Evidence

- `Invalid command!` when sending `open_chest()` before clearing the list.
- The service banner and prompt.
- The chest contents kept in `private/`.

## Lessons learned

- **Filtering names is not isolation**: as long as the interpreter is shared, the attacker can modify the filter itself.
- **Methods dodge brackets**: `clear()` needs neither `[]` nor quotes, exactly what the list blocked.
- **One exception ends the session**: test locally first; a syntax error remotely kills the process.

## Mitigations and detection

- Never run user input through `exec`/`eval`: no blacklist is reliable.
- If a restricted interpreter is required, use an unprivileged subprocess with no sensitive files and `seccomp`/a container; never the same process.
- Detection: services calling `exec` on `input()` and comparing against a string list; in logs, commands with `clear()`, `__builtins__` or `getattr` signal a jailbreak.

## References

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BEasy%5D%20Locked%20Away>
- <https://blog.ikuamike.io/posts/2024/htb_business_ctf_2024_misc>
- <https://docs.python.org/3/library/functions.html#exec>
