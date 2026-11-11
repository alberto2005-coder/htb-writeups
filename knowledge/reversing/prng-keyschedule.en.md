---
title: PRNG, seeds and key schedules
tags: [reversing, prng, rand, glibc, ctypes, ctf]
---

# PRNG, seeds and key schedules

**English** | [🇪🇸 Español](prng-keyschedule.md)

## 1. When to look here

A binary calls `srand`/`rand` and the result decides whether the input is correct, or it stores the seed next to the ciphertext. Two patterns:

- `srand(input); if (rand() != table[i])`: the secret is the seed and it falls to brute force.
- `srand(time(NULL))` with the seed written into the file: the encryption is reversible.

Before writing anything, check which PRNG is in play:

```bash
strings -n 5 binary | grep -E "srand|rand|time|random"
objdump -d -M intel binary | grep -E "call.*(srand|rand)"
```

## 2. glibc `rand()`

`rand()` is not a cryptographic generator: in glibc it is an additive feedback generator (`TYPE_3` algorithm) with per-process state. `srand(seed)` fixes that state and the sequence is **deterministic** for the same seed and the same libc.

```c
srand(seed);
int r1 = rand();   // 0 .. RAND_MAX (2^31 - 1 on glibc)
```

Practical consequences:

- glibc's sequence **does not match** the Windows CRT or Python's `random` (Mersenne Twister).
- For an ELF binary, reproduce with the Linux libc; for a PE, use the Windows CRT or an equivalent implementation.
- `rand()` yields 31 useful bits; a byte comes from `rand() & 0xff`.

## 3. Reproducing the sequence from Python

`ctypes` calls the system libc, the same one the binary uses:

```python
import ctypes

libc = ctypes.CDLL("libc.so.6")
libc.srand(1234)
print([libc.rand() for _ in range(5)])
```

To invert a seed mapping (FlagCasino), generate the first `rand()` of every printable seed and store it in a dictionary:

```python
mapping = {}
for c in range(0x20, 0x7f):
    libc.srand(c)
    mapping[libc.rand()] = chr(c)
```

## 4. Seed inside the file

If the format is `[4-byte seed][ciphertext]`, read the seed as a little-endian integer and replay the sequence:

```python
raw = open("flag.enc", "rb").read()
seed = int.from_bytes(raw[:4], "little")
libc.srand(seed)
for b in raw[4:]:
    ...
```

Each byte may consume **one or two** `rand()` outputs depending on the scheme (XOR plus rotation, for instance). Follow the binary's exact order and undo it backwards.

## 5. Rotations

`ROL8(b, k)` is not `b << k`: bits leaving on the left come back on the right.

```python
def rol(b, k):
    k &= 7
    return ((b << k) | (b >> (8 - k))) & 0xff

def ror(b, k):
    k &= 7
    return ((b >> k) | (b << (8 - k))) & 0xff
```

With `k = 0`, `b << 8` masks away and the byte is unchanged; handling it explicitly avoids relying on the mask.

## 6. Mersenne Twister and `randcrack`

When the target is Python (`random`) or a service leaking MT19937 outputs, guessing the seed is not enough: **624 32-bit outputs** rebuild the internal state and predict the rest.

```bash
pip install randcrack
```

```python
from randcrack import RandCrack
rc = RandCrack()
for value in outputs[:624]:
    rc.submit(value)
print(rc.predict_getrandbits(32))
```

## 7. Typical errors

- **Reproducing on another OS**: the sequence changes; check `file` and use the right libc.
- **Consuming one output per byte**: if the binary calls `rand()` twice, everything after the first byte is misaligned.
- **Confusing shift with rotation**: bits are lost and the text comes out "almost" readable.
- **Misread seed**: `int.from_bytes(..., "little")` versus big-endian; try both when output is garbage.
- **Different `RAND_MAX`**: assuming 32 bits when the libc returns 31 changes the masks.

## 8. Detection and mitigation (real world)

- A PRNG is not a CSPRNG: tokens, keys and nonces belong to `secrets`, `os.urandom` or the system CSPRNG.
- Never store the seed next to the ciphertext or seed from the clock: it turns encryption into a reversible encoding.
- Detection: files with a plausible UNIX timestamp in the first 4 bytes followed by high-entropy data; binaries with `srand`/`rand` on the validation path.

MITRE: T1027 (obfuscation), T1140 (deobfuscation). References: `man 3 rand`, glibc's `random_r.c` and the `randcrack` documentation.
