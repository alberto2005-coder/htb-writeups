---
challenge: Digital Cube
type: Stego
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [stego, qr, binary, images]
---

# Digital Cube — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The provided file contains binary data that forms a QR code when rendered at the right width. Adjusting the editor width or line length produces a readable image that can be scanned with a phone.

## Brief and surface

- Stego, Easy, retired.
- A file with binary data or a corrupted image is provided.
- No service to exploit.

```bash
file digital_cube
xxd digital_cube | head
```

## Recon

The content is neither readable text nor a standard image. Printing it in a monospaced editor with a fixed width makes `0`/`1` characters or colour blocks form a square pattern.

```bash
wc -c digital_cube
```

Try line widths that are multiples of the pattern size (for example 29, 33, 45) until the image is square.

## Analysis

If the file holds bytes, convert it to a 1-bit image:

```python
from PIL import Image
data = open('digital_cube','rb').read()
# estimate width from the square root of the bit count
```

If it holds binary text, adjust the editor width until the QR is readable. The QR decodes to the flag.

## The bug

The information is visually encoded, not encrypted. Anyone who finds the right geometry can rebuild it without a key.

## Local reproduction

1. Identify the data type.
2. Compute a square width.
3. Render it in black and white.
4. Scan the QR with `zbarimg` or a phone.

```bash
zbarimg qr.png
```

## Evidence

- `file`/`xxd` of the file.
- Reconstructed image.
- Decoded text with the flag redacted.

## Lessons learned

- Visual data depends on rendering width.
- A QR can look “broken” only due to formatting.
- Simple tools (`zbarimg`) solve the final step.
- Visual steganography is not encryption.

## Mitigation and detection

- Do not use images as the only secret channel.
- If required, encrypt content before encoding.
- Validate image formats on upload.
- In CTFs, review dimensions and repeated patterns.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/stego/digital-cube/>
- <https://github.com/mchehab/zbar>
- <https://en.wikipedia.org/wiki/QR_code>
