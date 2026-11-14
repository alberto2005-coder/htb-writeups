---
challenge: HM74
type: Hardware
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [hardware, hamming-code, error-correction, encoding]
---

# HM74 — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The challenge provides a noisy bit stream. Each seven-bit block is a Hamming(7,4) code: four data bits and three parity bits. Correcting the bad bit in each block and concatenating the data recovers the message.

## Prompt and surface

- Hardware, Very Easy, retired.
- A text file with bits is provided.
- The name `HM74` points to Hamming(7,4).

## Reconnaissance

```bash
file hm74.txt
head -3 hm74.txt
wc -c hm74.txt
```

- Bits and separators only.
- Length is a multiple of 7 once spaces are ignored.
- No binary to run.

## Code analysis

Hamming(7,4) encodes 4 data bits in 7 positions. Positions 1, 2 and 4 are parity; 3, 5, 6 and 7 are data. The three checks form a syndrome that identifies the bad bit (0 means no error).

## Why it works

This is not a vulnerability but an error-correction exercise. Noise flips one bit per block; without correction the data is not readable ASCII.

## Local reproduction

```python
blocks = [b for b in bits if len(b) == 7]
for b in blocks:
    p1 = int(b[0]) ^ int(b[2]) ^ int(b[4]) ^ int(b[6])
    p2 = int(b[1]) ^ int(b[2]) ^ int(b[5]) ^ int(b[6])
    p4 = int(b[3]) ^ int(b[4]) ^ int(b[5]) ^ int(b[6])
    syndrome = p1 + 2*p2 + 4*p4
    if syndrome:
        b = flip(b, syndrome - 1)
    data += b[2] + b[4] + b[5] + b[6]
```

Group data bits into bytes and decode ASCII.

## Exploitation

```bash
python solve.py hm74.txt
```

The script prints the message; the flag is redacted.

## Evidence

- Block length distribution.
- Non-zero syndromes and corrected positions.
- Resulting ASCII text.

## Lessons learned

- Block codes detect and correct errors.
- A syndrome is not a hash: it identifies a position.
- Validate parity before interpreting data.

## Mitigations and detection

- Use CRC or ECC suited to the medium.
- Do not confuse error correction with cryptographic integrity.
- Document the encoding scheme.

## References

- <https://www.hackthebox.com/challenges/HM74>
- <https://en.wikipedia.org/wiki/Hamming(7,4)>
