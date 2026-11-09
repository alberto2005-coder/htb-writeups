---
title: XOR and encoding chains (CTF and forensics)
tags: [crypto, xor, base64, hex, forensics]
---

# XOR and encoding chains

**English** | [🇪🇸 Español](xor-and-encodings.md)

## 1. When to look here

Very easy crypto challenges and forensic artefacts share one pattern: a blob that is "nothing" until a trivial XOR key is applied or two encodings are chained. Identify the file before writing a script:

```bash
file blob.bin
xxd blob.bin | head
```

High entropy with repeated structure suggests XOR. A blob made only of `A-Za-z0-9+/` and `=` is base64.

## 2. Single-byte XOR

Brute-force 256 keys and score for printable output:

```python
data = open('blob.bin','rb').read()
for k in range(256):
    out = bytes(b ^ k for b in data)
    if out.count(b'flag{') or out.startswith(b'PK\x03\x04') or out.startswith(b'\x89PNG'):
        print(k, out[:80]); open(f'x_{k}.bin','wb').write(out)
```

The tell is in the **magic bytes**: `PK\x03\x04` (ZIP), `%PDF`, `\xd0\xcf\x11\xe0` (OLE), `\x89PNG`. XORing a whole file with `0xFF` into a ZIP is the classic "Took the Byte" case.

## 3. Repeating-key XOR

With a known prefix (`flag{`, `picoCTF{`) you recover the key:

```python
ct = open('cipher.bin','rb').read()
known = b'flag{'
key = bytes(c ^ p for c, p in zip(ct, known))
print(key)   # repeats the pattern up to the real length
```

Once the key is shorter than the message, repeat it and decrypt:

```python
key = b'<key>'
pt = bytes(c ^ key[i % len(key)] for i, c in enumerate(ct))
print(pt)
```

Without a known prefix, try lengths 1–32 and keep whichever yields readable text (space and letter frequency). `xortool` automates it:

```bash
xortool cipher.bin -c 20 -l 8
```

## 4. Chained encodings

Typical order: **hex → base64 → text**, or the reverse. Detect by alphabet:

```python
import base64, binascii, string

def decode(s):
    s = s.strip()
    for name, fn in [('hex', binascii.unhexlify), ('b64', base64.b64decode)]:
        try:
            out = fn(s)
            if all(chr(b) in string.printable for b in out):
                print(name, out[:100]); return out
        except Exception:
            pass
```

Loop until nothing changes. CyberChef's *Magic* does the same by eye when there are few layers.

## 5. Typical errors

- **`binascii.Error: Invalid base64`** → stray newlines or URL-safe alphabet (`-`/`_`): use `base64.urlsafe_b64decode` and strip whitespace.
- **Wrong XOR key yields "almost readable" text** → the key length is a multiple; try divisor lengths.
- **Decrypted ZIP is corrupt** → XOR hit only the header; check whether the key changes midway or there is an unencrypted prefix.
- **`file` says `data`** → expected with XOR; do not trust it, brute-force anyway.

## 6. Detection and mitigation (real world)

- Single-byte XOR is not encryption: DLP catches it by entropy and by magic bytes after transformation.
- In malware, strings are obfuscated with XOR + base64; family YARA rules usually match the decoder routine, not the key.
- For forensics: keep the original blob, the script and the key; chain of custody includes the transformation.

MITRE: T1027 (obfuscation), T1140 (deobfuscation).
