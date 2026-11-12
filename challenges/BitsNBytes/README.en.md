---
challenge: BitsNBytes
type: Stego
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [stego, png, images, stegsolve, bit-planes, base64]
---

# BitsNBytes — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; not played on this profile.
> No flag or real bits.

## TL;DR

The challenge provides two PNGs that look identical. Combining them in **StegSolve** with **Image Combiner → SUB** reveals a vertical line of pixels. Read as bits and grouped into bytes, that line yields Base64 that decodes the flag.

## 1. Triage

```bash
file *.png
identify -verbose *.png | grep -E 'Geometry|Colorspace|Depth'
exiftool *.png
pngcheck -v *.png
sha256sum *.png
```

Both files have the same size and dimensions but different hashes: pixel data differs. `binwalk` and `zsteg` show nothing obvious, so comparison is the path.

## 2. Compare the images

```bash
compare -metric AE image1.png image2.png diff.png
```

`compare` counts differing pixels. To see where:

```bash
convert image1.png image2.png -compose difference -composite diff.png
```

The difference is concentrated in a strip. If the viewer hides it, zoom in:

```bash
convert diff.png -crop 40x512+0+0 +repage -scale 800% diff_zoom.png
```

## 3. StegSolve Image Combiner

In StegSolve:

1. `File` → open `image1.png`.
2. `Analyse` → `Image Combiner` → pick `image2.png`.
3. Try `SUB`, `ADD`, `XOR`, `AND`, `OR`.
4. Save the result.

With `SUB`, matching areas go black and the modified pixel line stands out. It is often in the first column or row; scan the whole result.

## 4. Pixels to bits

Extract the vertical line. Reduce each pixel to one bit: black = `0`, white = `1` (try the inverse too). Group 8 bits per byte, MSB first:

```python
from PIL import Image

img = Image.open('diff.png').convert('RGB')
w, h = img.size
bits = []
for y in range(h):
    r, g, b = img.getpixel((0, y))
    bits.append('1' if (r + g + b) > 0 else '0')

data = ''.join(bits)
out = bytes(int(data[i:i+8], 2) for i in range(0, len(data) - 7, 8))
print(out[:120])
```

The output starts with printable characters; if not, invert bit order or read the first row instead of the column.

## 5. Base64

The extracted string is usually Base64:

```bash
echo '<BASE64>' | base64 -d
```

If it looks like Base64 but fails, check padding (`=`), strip newlines and try URL-safe variants (`-`/`_`).

## 6. Common mistakes

- **`compare` returns 0** → wrong images or they were recompressed.
- **The line is invisible** → try `ADD`/`XOR` and inspect each channel.
- **Bits make no sense** → invert 0/1, try the red-channel LSB or read the row instead of the column.
- **Invalid Base64** → missing padding bits or an included header.
- **The image went through an editor** → recompression destroys the difference.

## Lessons learned

- Two “identical” images with different hashes always deserve a diff.
- StegSolve Image Combiner is faster than writing the diff by hand.
- Data may sit in a single row or column, not the whole image.
- A bitstream is rarely text: try order, polarity and grouping.
- Base64 is the natural next step, not the end.

## Mitigations (for challenges)

- Do not recompress PNGs before analysis.
- Keep originals and work on copies.
- Record the exact StegSolve operation and line orientation.

MITRE: T1027.003.

## References

- <https://insanitys.medium.com/hack-the-box-retired-stego-challenges-36ccc5f3dab1>
- <https://github.com/Giotino/stegsolve>
- <https://imagemagick.org/script/compare.php>
