---
challenge: Took the Byte
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, xor, zip, magic-bytes, cyberchef]
---

# Took the Byte — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

You get a file called `password` that nothing will open. Its content is almost all `0xFF`: an **XOR with key `0xFF`** revives it into a **ZIP** holding `password.txt`, which contains the flag.

## Evidence

- A single file, `password`, with no useful extension.

## Method

1. **Identify it**:

```bash
file password
xxd password | head
binwalk password
```

`file` does not recognise it and `xxd` shows a wall of `ff`: the classic signature of a single-byte XOR with `0xFF`.

2. **Apply the XOR** (the challenge name is the hint: "took a byte"):

```bash
python3 -c "d=open('password','rb').read(); open('out','wb').write(bytes(b^0xFF for b in d))"
file out
```

3. **Open the resulting ZIP**:

```bash
unzip out
cat password.txt
```

The flag is in the text. In CyberChef it is *XOR* with key `ff` followed by *Unzip*.

4. **Signature check**: a ZIP starts with `PK\x03\x04`; if it is absent after the XOR, the wrong key was used (try `0x00`, `0xFF` and a one-byte bruteforce).

## Pitfalls

- **Expecting cryptography**: it is a one-byte XOR; no passwords, no `rockyou`.
- **`strings`**: on the raw file it shows nothing useful and misleads.
- **One byte off**: if the ZIP comes out corrupt, check the XOR was applied to the whole file, not just the header.

## Lessons

- A single-byte XOR is spotted by value repetition and broken by trying 256 keys.
- A format signature (`PK`, `%PDF`, `\x89PNG`) verifies the transform was right.
- "Obfuscated" is not "encrypted": one byte separates noise from the original file.
