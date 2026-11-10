---
challenge: Makeshift
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, custom-cipher, permutation]
---

# Makeshift — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A home-made "cipher": reverse the string, then permute each three-character block as `b, c, a`. Both operations invert, so undo them in reverse order: permutation first, then reversal.

## Brief

The challenge ships `source.py` and `output.txt`:

```python
flag = FLAG[::-1]
new_flag = ''
for i in range(0, len(flag), 3):
    new_flag += flag[i+1]
    new_flag += flag[i+2]
    new_flag += flag[i]
print(new_flag)
```

No key, no server: this is an inversion exercise, not cryptanalysis.

## Recon

```bash
cat output.txt
# !?}De!e3d_5n_nipaOw_3eTR3bt4{_THB
wc -c output.txt
```

The string starts with `!?}` and ends with `_THB`: the flag is reversed and permuted.

## The flaw

Two trivial layers:

1. **Reversal**: `FLAG[::-1]` flips the whole string.
2. **Triplet permutation**: from `(a, b, c)` it emits `b, c, a`.

The code is readable as-is; the work is writing the inverse without tripping over indices.

## Exploitation

```python
c = open("output.txt").read().strip()
restored = [''] * len(c)

j = 0
for i in range(0, len(c), 3):
    restored[i + 1] = c[j];     j += 1
    restored[i + 2] = c[j];     j += 1
    restored[i]     = c[j];     j += 1

print(''.join(restored)[::-1])
```

```text
HTB{<flag>}
```

Check: the result must start with `HTB{`. A one-character shift means `i+1` was assigned where `i` belonged.

## Evidence

- Trimmed output; no flags.

## Lessons

- **Layer order**: reversing then permuting (or the other way round) yields garbage; undo from the inside out.
- **Length not a multiple of three**: the original loop would raise `IndexError`; here it is a multiple.
- **Indices**: a mutable list avoids the classic `string index out of range`.
- **Not ROT**: no letter substitution, only position.

- A keyless home-made "cipher" gives no confidentiality: it is a permutation.
- With the code in hand, the task is careful inversion, not cryptanalysis.
- Mitigation: standard authenticated encryption (AES-GCM, ChaCha20-Poly1305), never custom algorithms.
