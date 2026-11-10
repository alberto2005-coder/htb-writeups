---
challenge: Ancient Encodings
category: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, base64, hex, encodings]
---

# Ancient Encodings — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

`source.py` reveals the "cipher": `hex(bytes_to_long(b64encode(FLAG)))`. No key, no real cryptography: **base64** then **hex**. Undo it in reverse order.

## Evidence

- `source.py` and `output.txt` (one huge hex integer).

## Method

1. **Read the cipher**:

```python
from Crypto.Util.number import bytes_to_long
from base64 import b64encode

def encode(message):
    return hex(bytes_to_long(b64encode(message)))
```

2. **Undo it**: hex → bytes → base64 → text.

```python
from Crypto.Util.number import long_to_bytes
from base64 import b64decode

data = open("output.txt").read().strip()
print(b64decode(long_to_bytes(int(data, 16))).decode())
```

3. **CyberChef equivalent**: `From Hex` → `From Base64` → `To Text`.

## Pitfalls

- **Stripping `0x`**: `int(..., 16)` accepts the prefix, `bytes.fromhex` does not.
- **Newlines** in `output.txt`: call `strip()`.

## Lessons

- Base64 and hex are **encodings**, not encryption: reversible without a key.
- Identifying a layer by its alphabet (`A-Za-z0-9+/=` versus `0-9a-f`) saves time.
- In CTFs, `source.py` is the spec: read it before reaching for tools.
