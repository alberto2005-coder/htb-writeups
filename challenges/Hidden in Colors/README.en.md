---
challenge: Hidden in Colors
type: Stego
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [stego, image, png, colours, hex, mapping]
---

# Hidden in Colors — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

The image does not hide data in the least significant bits: **each pixel's colour value is the data**. The colours are artificially chosen (few tones, suspiciously clean hexadecimal values), and the message is recovered by mapping those colour codes to characters. This is a **Hard stego** challenge, not a one-command `zsteg`.

## Brief

"We intercepted this weird image coming from a…": a single PNG is provided. No password, no application; the artifact is the whole challenge.

## Recon

```bash
file image.png
exiftool image.png
pngcheck -v image.png
zsteg -a image.png | head -30
```

Expect a valid PNG, no useful metadata and no readable LSB. If `zsteg` returns no text, the LSB hypothesis is dead and the **colour values** are next.

## The flaw

Opening the image shows flat colour blocks, not a photo. The pixels use a very small palette and their `#RRGGBB` codes follow a sequence instead of a natural distribution. That is the channel: **the data is encoded in the colour, not in the low bit**.

## Exploitation

1. **List the colours** by frequency or appearance order — GIMP (eyedropper plus palette), StegOnline's "Extract RGBA values", or Python:

```python
from PIL import Image
im = Image.open("image.png").convert("RGB")
seen, order = set(), []
for px in im.getdata():
    if px not in seen:
        seen.add(px); order.append(px)
print(len(order), order[:16])
```

2. **Map each colour to a value**: with a few dozen colours each one can be an ASCII character or a nibble; with 256, each colour is a byte derived from `0xRRGGBB`.

```python
codes = ["%02x%02x%02x" % px for px in order]
print("".join(chr(int(c, 16) % 256) for c in codes)[:200])
```

3. **Rebuild the order**: the message usually reads in raster order (row by row); if the text comes out scrambled, try column order or the reverse.

```python
data = "".join(chr(px[0]) for px in im.getdata() if px != (0, 0, 0))
print(data[:120])
```

4. **Verify**: the output must start with the flag prefix (`HTB{`). When it does, the mapping is right.

## Evidence

- Trimmed output of the key commands; no flags or tokens.
- Real values live in `private/` and are not published.

## Lessons

- **Rule out LSB first** with `zsteg -a`: if there is no text, the channel is something else.
- **Pretty colours are a hint**: an artificial palette betrays value-level encoding.
- **Order matters**: the right map with the wrong traversal still yields garbage.

- In stego, the default tool is not the default answer.
- A few flat colours is a data file in disguise.
- Mitigation: palette and entropy analysis catch covert channels; signatures do not.

## Verification note

HTB rates this **Hard** and the official walkthrough works through "mapping colour hex codes"; no detailed step-by-step public writeup exists, so the steps above describe the technique rather than transcribe an answer.
