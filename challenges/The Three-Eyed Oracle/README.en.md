---
challenge: The Three-Eyed Oracle
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, aes, ecb, oracle, byte-at-a-time]
---

# The Three-Eyed Oracle — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

An oracle encrypts `input || flag` with AES-ECB under a fixed key. By choosing the prefix, each unknown byte is aligned with a block boundary and compared against a 256-entry dictionary. It is a byte-at-a-time attack.

## Prompt and surface

- Crypto, Easy, retired.
- A service returns the ciphertext in hex.
- The key is not provided.

## Reconnaissance

```bash
nc <IP> <PORT>
```

- Every input returns a ciphertext.
- The same prefix yields the same block: ECB.
- Length grows in 16-byte blocks.

## Code analysis

The service computes `AES-ECB(key, user_input + flag)`. ECB encrypts each 16-byte block independently, so equal blocks produce equal ciphertext. There is no IV or random padding.

## Why it works

Send a 15-byte prefix so the first flag byte lands at the end of a block. The oracle returns that block; try every possible byte as the last prefix byte and compare. Once a byte is known, shorten the prefix and repeat.

## Local reproduction

```python
def oracle(prefix):
    return encrypt(prefix + flag)

known = b''
for i in range(len(flag)):
    pad = b'A' * (15 - len(known) % 16)
    target = oracle(pad)[:16]
    for c in range(256):
        if oracle(pad + known + bytes([c]))[:16] == target:
            known += bytes([c])
            break
```

## Exploitation

```bash
python solve.py --host <IP> --port <PORT>
```

The script prints the flag; it is redacted.

## Evidence

- Repeated blocks for the same prefix.
- Length in multiples of 16.
- Recovered byte by comparison.

## Lessons learned

- ECB leaks plaintext structure.
- An encryption oracle enables byte-at-a-time recovery.
- A controllable prefix breaks confidentiality.

## Mitigations and detection

- Use AES-GCM or CBC with a random IV and a MAC.
- Never concatenate user input with secrets.
- Rate-limit and monitor repetitive query patterns.

## References

- <https://www.hackthebox.com/challenges/The%20Three-Eyed%20Oracle>
- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/the-three-eyed-oracle/>
- <https://cryptopals.com/sets/2/challenges/12>
