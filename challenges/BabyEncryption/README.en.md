---
challenge: BabyEncryption
category: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, affine, modular-inverse, python]
---

# BabyEncryption — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

You get `chall.py` and `msg.enc`. The cipher is school arithmetic on each byte: `((123 * c) + 18) % 256`. That is an **affine** map over `Z/256`, so it inverts by multiplying with 123's modular inverse, which is **179** (since `123 * 179 ≡ 1 mod 256`).

## Evidence

- `chall.py` (the cipher) and `msg.enc` (binary ciphertext).

## Method

1. **Read the cipher**:

```python
def encryption(msg):
    ct = []
    for char in msg:
        ct.append(((123 * char) + 18) % 256)
    return bytes(ct)
```

2. **Invert in reverse order**: subtract 18 first, then multiply by the inverse.

```python
def decryption(msg):
    return bytes((179 * (c - 18)) % 256 for c in msg)

print(decryption(open("msg.enc", "rb").read()).decode())
```

3. **Check** the output starts with `HTB{`; otherwise the modulus or shift was mistyped.

## Pitfalls

- **`pow(123, -1, 256)`**: available from Python 3.8; otherwise compute it by hand (179).
- **Multiplying before subtracting**: reversing the order yields garbage.
- **Binary `msg.enc`**: open it with `rb`, never as text.

## Lessons

- Any affine map `a*x + b (mod m)` is reversible when `gcd(a, m) = 1`.
- A keyless "custom cipher" is an encoding: break it with algebra, not brute force.
- Checking against the known flag prefix is the fastest test.
