---
challenge: Baby Crypt
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, xor, ghidra, gdb]
---

# Baby Crypt — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real flags.

## TL;DR

An ELF asks for a three-byte key and XOR-decrypts a 26-byte block. The ciphertext is in the binary and the expected plaintext starts with HTB's flag prefix (`HTB` + `{`), so the first three key bytes are `key[i] = ciphertext[i] ^ plaintext[i]`. With key `w0w` the program prints the flag.

## Brief and surface

- Reversing, Easy, retired.
- A single `baby_crypt` binary is provided.
- No server: everything runs locally.

```bash
file baby_crypt
checksec --file=baby_crypt
```

```text
ELF 64-bit LSB shared object, x86-64, not stripped
```

## Recon

The binary is not stripped, so `main` is visible in Ghidra. `strings` is also a good start:

```bash
strings -a baby_crypt | head -30
```

The prompt and error message are visible, but the flag is not: it is computed at runtime.

## Source analysis

The main function allocates 4 bytes for the key, reads up to 3 characters and XORs a local block:

```c
key = malloc(4);
fgets(key, 4, stdin);

local_38 = 0x6f0547480c35643f;
local_30 = 0x28130304026f0446;
local_28 = 0x05000f4358280e52;
local_20 = 0x4d56;

for (i = 0; i < 0x1a; i++)
    *((byte *)&local_38 + i) ^= key[i % 3];

printf("%.26s\n", &local_38);
```

The block is little-endian. The first ciphertext bytes are `3f 64 35 ...`; the expected plaintext starts with `H T B`.

## The bug

XOR is symmetric: `c = p ^ k` means `k = c ^ p`. Since the flag format is known, no brute force is needed. The program implicitly checks the result by printing it; the right key produces readable text.

```text
k[0] = 0x3f ^ ord('H') = 'w'
k[1] = 0x64 ^ ord('T') = '0'
k[2] = 0x35 ^ ord('B') = 'w'
```

## Local reproduction

```bash
chmod +x baby_crypt
./baby_crypt
# Give me the key and I'll give you the flag:
w0w
```

Verify without running:

```python
ct = bytes.fromhex('3f6435...')   # 26 bytes
key = bytes([ct[0]^ord('H'), ct[1]^ord('T'), ct[2]^ord('B')])
pt = bytes(b ^ key[i % 3] for i, b in enumerate(ct))
print(pt.decode())
```

In Ghidra, rename the buffer and retype it as `char[26]` to read the whole block.

## Exploitation

There is no remote exploit: "exploitation" is recovering the key and running the binary.

```bash
printf 'w0w\n' | ./baby_crypt
```

The correct output contains the flag; redact it in evidence.

## Evidence

- Decompiled `main` with the XOR loop.
- Calculation of the three key bytes.
- Run with `w0w` and the flag redacted.

## Lessons learned

- Repeating-key XOR with known plaintext breaks without brute force.
- The flag format is a three-byte known plaintext.
- Little-endian matters when reading 64-bit constants.
- Ghidra and `gdb` are enough; no reversing framework is required.

## Mitigations and detection

- Do not use short-key XOR to protect secrets.
- If obfuscating a check, do not store the expected plaintext in the same binary.
- For CTFs, document the exact constant and build offset.
- In real software, use AES-GCM or ChaCha20-Poly1305 with keys managed outside the binary.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/baby-crypt/>
- <https://ghidra-sre.org/>
- <https://sourceware.org/gdb/current/onlinedocs/gdb/>
