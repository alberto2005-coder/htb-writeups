---
challenge: Baby RE
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, ltrace, strcmp, dynamic-analysis]
---

# Baby RE — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The binary asks for a key and compares it with `strcmp`. `ltrace` shows the call and the expected value without decompiling. Entering that key prints the flag.

## Statement and surface

- Reversing, Very Easy, retired.
- An ELF executable named `baby` is provided.
- The program reads a key from standard input.

```bash
file baby
./baby
```

## Reconnaissance

- 64-bit ELF, not stripped, dynamically linked.
- `strings` shows the prompt and the error message.
- `checksec` reports the protections; they are not the obstacle in this challenge.

```bash
strings -n 5 baby | head
checksec --file=baby
```

## Code analysis

The main function reads input with `fgets` and compares it with a constant string using `strcmp`. The string lives in `.rodata` and also appears in the dynamic trace.

```bash
ltrace ./baby
```

The output shows:

```text
strcmp("<INPUT>", "<KEY>")
```

## Why it works

Validation is a local comparison. There is no obfuscation or remote check: the expected value is in the binary and can be extracted with `strings`, `ltrace`, a debugger or Ghidra. The key is not a cryptographic secret.

## Local reproduction

```bash
chmod +x baby
printf '<KEY>\n' | ./baby
```

- `ltrace` requires the binary to be executable.
- If the input includes a newline, `fgets` keeps it and `strcmp` compares against the expected string.

## Exploitation

1. Run `ltrace ./baby`.
2. Enter any value.
3. Read the second string in the `strcmp` call.
4. Repeat with that key.

```bash
printf '<KEY>\n' | ./baby
```

The program prints the flag; it is redacted.

## Evidence

- `ltrace` output with the key redacted.
- Successful run and redacted flag.
- `file` and `strings` output for the binary.

## Lessons learned

- A local comparison does not protect a secret.
- `ltrace` is enough when the binary uses library functions.
- `strings` and Ghidra reach the same result without running it.

## Mitigations and detection

- Do not store keys or flags in the client.
- Validate on the server and use an authenticated protocol.
- Obfuscation is not a secure design, but it raises the cost.
- For challenges, rotate the expected value and never reuse it in production.

## References

- <https://www.hackthebox.com/challenges/Baby%20RE>
- <https://man7.org/linux/man-pages/man1/ltrace.1.html>
- <https://attack.mitre.org/techniques/T1027/>
