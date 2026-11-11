---
challenge: Simple Encryptor
category: Reversing
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, prng, xor, rotation, ctypes]
---

# Simple Encryptor — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

The challenge ships `encrypt` and `flag.enc`. The binary reads `flag`, seeds `srand(time(NULL))`, encrypts each byte with `b ^= rand()` followed by `ROL(b, rand() & 7)`, and writes **the seed in the first four bytes** of the file. With that seed the sequence can be reproduced and the encryption reversed: `ROR` then XOR. It must be done against glibc.

## Brief and surface

- Reversing, Very Easy.
- Files: `encrypt` (64-bit ELF) and `flag.enc`.
- The story is ransomware: the original flag is gone, but both the encryptor and the encrypted file remain.

## Recon

```bash
file encrypt flag.enc
strings -n 6 encrypt | head
xxd flag.enc | head
```

`strings` shows `srand`, `fopen`, `ftell` and `time`: the PRNG hint. `flag.enc` starts with four non-text bytes; the rest is the ciphertext.

## Source analysis

The decompiled `main`, in Ghidra or IDA, does this in order:

```c
stream = fopen("flag", "rb");
fseek(stream, 0, SEEK_END);
size = ftell(stream);
fseek(stream, 0, SEEK_SET);
buf = malloc(size);
fread(buf, size, 1, stream);
fclose(stream);

seed = time(NULL);
srand(seed);
for (i = 0; i < size; i++) {
    buf[i] ^= rand();
    r = rand();
    buf[i] = ROL8(buf[i], r & 7);
}

out = fopen("flag.enc", "wb");
fwrite(&seed, 1, 4, out);
fwrite(buf, 1, size, out);
```

- The seed is stored in clear text at the start of the file: nothing to guess.
- Each byte consumes **two** `rand()` outputs: one for the XOR and one for the rotation.
- `ROL8` is a rotation, not a shift: bits leaving on the left re-enter on the right.

## The bug

The encryption is reversible with the seed, and the seed ships inside the file. XOR with `rand() & 0xff` plus a 0–7 bit rotation adds no secrecy: the only unknown was the PRNG state, which is handed over.

## Local reproduction

Recompile the encryptor from the pseudocode, encrypt a test `flag`, and check that the decryptor returns the same content. The original binary expects a file named `flag` in the current directory.

## Exploitation

Decryptor using `ctypes` against the system libc, the same one the binary uses:

```python
import ctypes

libc = ctypes.CDLL("libc.so.6")
raw = bytearray(open("flag.enc", "rb").read())

seed = int.from_bytes(raw[:4], "little")
libc.srand(seed)

out = bytearray()
for b in raw[4:]:
    r1 = libc.rand()
    r2 = libc.rand()
    k = r2 & 7
    b = ((b >> k) | (b << (8 - k))) & 0xff   # ROR
    out.append(b ^ (r1 & 0xff))

print(out.decode())
```

Notes:

- Order matters: decrypting undoes the rotation first, then the XOR.
- With `k = 0`, `b << 8` masks to `0xff` and the byte is unchanged.
- Python's `random` will not work: its Mersenne Twister is not C `rand()`. The Windows CRT is not either.

## Evidence

- `encrypt`, a dynamic 64-bit ELF.
- `flag.enc` with a 4-byte seed followed by the ciphertext.
- Decrypted text starting with the usual HTB prefix; kept in `private/`.

## Lessons learned

- **Read the seed from the file**: the first attempt tried timestamps near the challenge date; unnecessary.
- **Operation order**: XOR before `ROR` yields half-readable garbage.
- **Wrong PRNG**: `python -c "import random"` does not reproduce glibc `rand()`; call libc instead.

## Mitigations and detection

- Do not encrypt with a clock-seeded PRNG, and never store the seed next to the ciphertext: that turns encryption into a reversible encoding.
- For real encryption use AES-GCM or ChaCha20-Poly1305 with a random nonce and the key outside the artefact.
- Detection: files whose first 4 bytes are a plausible UNIX timestamp followed by high-entropy data; YARA on the `time`/`srand`/`fwrite` triad.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/simple-encryptor/>
- <https://blog.loganthompson.de/posts/htb-simple-encryptor>
- <https://man7.org/linux/man-pages/man3/rand.3.html>
