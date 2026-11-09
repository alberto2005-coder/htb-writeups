---
challenge: Makeshift
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, custom-cipher, permutation, reverse-engineering]
---

# Makeshift — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A three-line "cipher": reverse the string, then rotate each block of three characters. Both operations invert, so undo them in reverse order: permutation first, reversal last.

## Brief

```python
flag = FLAG[::-1]
new_flag = ''
for i in range(0, len(flag), 3):
    new_flag += flag[i+1]
    new_flag += flag[i+2]
    new_flag += flag[i]
print(new_flag)
```

The output is provided. There is no key.

## Analysis

Two layers, both trivial:

1. **Reversal**: `FLAG[::-1]` flips the whole string.
2. **Block permutation**: for each triple `(a, b, c)` it emits `b, c, a`.

The encryption reads directly; the work is writing its inverse without slipping on the indices.

## Exploitation

Undo from the inside out: permutation first, then reversal.

```python
c = "<ciphertext>"
restored = [''] * len(c)

j = 0
for i in range(0, len(c), 3):
    restored[i + 1] = c[j]; j += 1
    restored[i + 2] = c[j]; j += 1
    restored[i] = c[j]; j += 1

print(''.join(restored)[::-1])
```

Quick check: the result must start with `HTB{`. If it is off by one character, the bug is assigning to `i+1` where `i` belongs.

## Pitfalls

- **Length not a multiple of three**: the original loop would raise `IndexError`; handle padding first.
- **Layer order**: reversing then permuting yields garbage; it is the other way round.
- **Indices**: a mutable list avoids the classic `string index out of range`.
- **Mistaking it for ROT**: no letter substitution here, only position.

## Lessons

- A keyless "custom cipher" gives no confidentiality: it is a permutation.
- With the code in hand, the challenge is inverting carefully, not cryptanalysis.
- Mitigation: standard authenticated encryption (AES-GCM, ChaCha20-Poly1305), never homegrown algorithms.
