---
challenge: Hidden in Colors
type: Stego
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [stego, image, lsb, png, zsteg]
---

# Hidden in Colors — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

## Brief

A seemingly normal PNG hides data in its least significant bits. No password and no hint: extract the hidden layer.

## Triage

```bash
file image.png
exiftool image.png
pngcheck -v image.png
binwalk image.png
```

- `exiftool` for metadata and comments.
- `pngcheck` spots odd chunks (tEXt, zTXt, iTXt) and CRC errors.
- `binwalk` flags an embedded ZIP or other file.

## Extraction

1. **LSB with `zsteg`** (the most direct on PNG/BMP):

   ```bash
   zsteg image.png
   zsteg -a image.png       # every combination
   ```

2. **`steghide`** for JPEG or when a password exists:

   ```bash
   steghide extract -sf image.jpg
   ```

3. **Bit by bit** in Python when `zsteg` finds nothing:

   ```python
   from PIL import Image
   im = Image.open('image.png').convert('RGB')
   bits = [str(p[i] & 1) for p in im.getdata() for i in range(3)]
   data = bytes(int(''.join(bits[i:i+8]), 2) for i in range(0, len(bits)-7, 8))
   print(data[:200])
   ```

4. **Channels and order**: try R, G, B, alpha, RGB/BGR order and least vs most significant bit.

## Findings (pattern)

```text
zsteg: b1,rgb,lsb,xy  .. text: "HTB{...}"
```

The string appears when reading bit 1 of the RGB channels in xy order; if you get noise, change channel or order.

## Typical errors

- **`zsteg` finds nothing** → the image may be JPEG (use `steghide`) or the payload sits in the alpha channel.
- **Encrypted text** → there is a password; try `steghide` with a wordlist or look for the key in metadata.
- **Invalid CRC** → the image was edited by hand; `pngcheck` says so and `binwalk` can extract the remainder.
- **Bits reversed** → invert the sequence or read right to left.

## Lessons

- Channel order matters as much as the chosen bit.
- `zsteg -a` is the first command, not the last.
- A PNG with a broken CRC is a clue, not a download error.

MITRE: T1027.003 (steganography).
