---
challenge: sekur julius
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, caesar, classical-cipher, bruteforce]
---

# sekur julius — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The text is encrypted with a Caesar variant. Trying all 25 shifts and scoring the output with a dictionary recovers the message and the flag.

## Prompt and surface

- Crypto, Easy, retired.
- A ciphertext is provided.
- The name alludes to Julius Caesar.

## Reconnaissance

```bash
cat ciphertext.txt
python3 - <<'PY'
from collections import Counter
print(Counter(open('ciphertext.txt').read()).most_common(8))
PY
```

- Letters only.
- Frequency suggests a fixed shift.
- No long key.

## Code analysis

Caesar computes `c = (p + k) mod 26`. The variant may reverse the alphabet or change the sign; both are covered by trying `k` from 0 to 25 and the reversed text.

## Why it works

The key space is only 26. There is no salt or diffusion, so letter frequency and common words identify the plaintext.

## Local reproduction

```python
def caesar(s, k):
    out = []
    for c in s:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            out.append(chr((ord(c) - base + k) % 26 + base))
        else:
            out.append(c)
    return ''.join(out)

for k in range(26):
    print(k, caesar(data, k))
```

## Exploitation

```bash
python solve.py
```

Pick the shift that produces readable words. The flag is redacted.

## Evidence

- Frequency distribution.
- Table of 26 candidates.
- Readable plaintext.

## Lessons learned

- Caesar is not modern encryption.
- A tiny key space invites brute force.
- Frequency and context resolve ambiguity.

## Mitigations and detection

- Use AES-GCM or ChaCha20-Poly1305 with managed keys.
- Do not confuse encoding with encryption.
- Train developers in applied cryptography.

## References

- <https://www.hackthebox.com/challenges/sekur%20julius>
- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/sekur-julius/>
