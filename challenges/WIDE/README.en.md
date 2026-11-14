---
challenge: WIDE
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, wide-strings, ghidra]
---

# WIDE — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The `wide` ELF compares input with UTF-16 strings. Plain `strings` does not show them fully; `strings -el` and a wide-string search in Ghidra reveal the comparison and the key.

## Prompt and surface

- Reversing, Very Easy, retired.
- A 64-bit ELF and a `db.ex` file are provided.
- The prompt mentions an encrypted dimension.

```bash
file wide db.ex
checksec ./wide
```

## Reconnaissance

```bash
strings -a wide | head
strings -a -el wide
```

- `wide` is not stripped.
- Readable strings are separated by null bytes.
- `db.ex` lists dimensions and codes.

## Code analysis

In Ghidra, main walks a table of names and compares input against each using a wide-string function. `Flaggle Alpha` is the only dimension marked encrypted.

The relevant comparison uses `wchar_t`/UTF-16, which is why normal `strings` only shows fragments.

## Why it works

The "encryption" is a direct comparison against an embedded string. There is no key derivation or cryptography: the key sits in `.rodata` as wide text.

## Local reproduction

```bash
chmod +x wide
./wide
# Try candidates and watch the comparison
```

- Set a breakpoint on the comparison in GDB.
- Inspect `$rdi`/`$rsi` as UTF-16 strings.
- Alternatively, dump `.rodata` and decode every other byte.

## Exploitation

```bash
strings -el wide | grep -i -E 'flag|dimension|alpha'
./wide
```

Enter the recovered string and the binary prints the flag. The flag is redacted.

## Evidence

- `file` and `checksec` output.
- `strings -el` with the candidate string.
- Ghidra screenshot of the comparison.
- Successful run without showing the flag.

## Lessons learned

- Default `strings` misses UTF-16.
- An "obfuscated" binary can still be a simple comparison.
- Check character width before concluding there is no text.

## Mitigations and detection

- Never store secrets in distributed binaries.
- Use key derivation and constant-time comparison for licence checks.
- Obfuscation is not a substitute for secure design.

## References

- <https://www.hackthebox.com/challenges/WIDE>
- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/wide/>
- <https://attack.mitre.org/techniques/T1027/>
