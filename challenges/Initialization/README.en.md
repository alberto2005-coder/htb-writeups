---
challenge: Initialization
type: Crypto
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [crypto, aes, ctr, key-reuse, python]
---

# Initialization — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

The challenge provides the code that encrypts several messages with AES-CTR. Key initialization shares one inner list through list aliasing, so every message uses the same key. With multiple ciphertexts and known counters, keystreams align and plaintext is recovered.

## Statement and surface

- Crypto, Medium, retired.
- `source.py`, `messages.txt` and `output.txt` are provided.
- Each output line is a hex-encoded ciphertext.

```bash
file source.py output.txt
head -2 output.txt
```

## Reconnaissance

- `source.py` imports `AES`, `Counter` and `pad`.
- `MSG` is loaded with `eval` from `messages.txt`.
- Each message is encrypted with one `KEYS` entry and its own `CTR`.

## Code analysis

The class creates `self.KEYS = [[b'\x00'] * 16] * len(MSG)`. List multiplication repeats the reference to the same inner list, so assigning `keys[i][j]` mutates every row. The result is one 16-byte key shared by all messages.

Counters are created with `Counter.new(128)`, but CTR encryption and key reuse allow keystreams to be related when message structure is known.

## Flaw explanation

Key entropy is not the issue: list aliasing is. Every message shares a key and the nonce is not managed as a unique, verified value. Two ciphertexts reveal the XOR of their plaintexts and enable known-plaintext recovery.

## Local reproduction

```bash
python3 source.py
# Compare the effective key of each message
```

## Exploitation

```python
from Crypto.Cipher import AES

# c1, c2: ciphertexts; k: recovered key
p1 = bytes(a ^ b for a, b in zip(c1, keystream))
```

Use a known message or repeated structure to obtain enough keystream bytes and rebuild the flag.

## Evidence

- Code with list aliasing.
- Identical effective keys.
- Recovered plaintext with the flag redacted.

## Lessons learned

- `[[x] * n] * m` shares the inner list.
- A shared key in CTR is a critical flaw.
- Known plaintext turns the cipher into a recoverable XOR.

## Mitigations and detection

- Generate independent keys with `os.urandom(16)` per message.
- Use AES-GCM or ChaCha20-Poly1305 with a unique nonce.
- Add tests comparing keys and nonces.
- References: NIST SP 800-38A, PyCryptodome, HTB Initialization.

## References

- <https://www.hackthebox.com/challenges/Initialization>
- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/initialization/>
- <https://csrc.nist.gov/pubs/sp/800/38/a/final>
- <https://attack.mitre.org/techniques/T1556/>
