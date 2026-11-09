# Steganography in images and audio

**English** | [🇪🇸 Español](images-audio.md)

Checklist for Stego challenges: what to check in an image or audio file before assuming there is nothing.

## 1. Images — triage

```bash
file image.*; exiftool image.*
pngcheck -v image.png
binwalk -e image.png
identify -verbose image.png | head -40
```

- EXIF comments (`Comment`, `UserComment`) and `tEXt`/`zTXt`.
- `binwalk` for a ZIP/PDF appended after `IEND`.
- Size differences against the original when the challenge provides one.

## 2. LSB and bit planes

```bash
zsteg image.png
zsteg -a image.png
```

`zsteg` reports combination (`b1,rgb,lsb,xy`), length and type. If nothing shows:

- Try each channel separately (`b1,r`, `b1,g`, `b1,b`, `b1,a`).
- Try MSB (`b8`) and `xy`/`yx` orders.
- Extract manually with Pillow and look for headers (`PK`, `%PDF`, `\x89PNG`) in the bitstream.

## 3. JPEG and passwords

```bash
steghide info image.jpg
steghide extract -sf image.jpg -p <pass>
stegseek image.jpg rockyou.txt
```

`stegseek` cracks `steghide` with a wordlist in seconds. If the brief hints at a phrase, try it as the password.

## 4. Compare two images

With an original and a modified copy:

```bash
compare -metric AE original.png modified.png diff.png
python3 - <<'PY'
from PIL import Image, ImageChops
a = Image.open('original.png').convert('RGB')
b = Image.open('modified.png').convert('RGB')
ImageChops.difference(a, b).save('diff.png')
PY
```

Zoom into the diff and look for pixels with non-zero difference.

## 5. Audio

```bash
soxi audio.wav
spectrogram audio.wav -o spec.png      # or Sonic Visualiser
```

- **Spectrogram**: text drawn at high frequencies, very common.
- **DTMF**: dial tones → `multimon-ng -a DTMF`.
- **Morse**: `sox audio.wav -n stat` and `multimon-ng -a MORSE`.
- **Sample LSB**: `wav2lsb` or a small `soundfile` script.
- **Metadata**: `exiftool`, `ffprobe -show_format`.

## 6. What not to do

- Do not send the image through social media: it recompresses and destroys the LSB.
- Do not assume `steghide` is the only tool; `outguess`, `openstego` and `stegolsb` exist too.
- Do not ignore the alpha channel: it is the usual hiding place after RGB.

## Lessons

- `zsteg -a` first, always.
- A diff between two image versions solves more challenges than any single tool.
- In audio, the spectrogram is the first stop, not the last.

MITRE: T1027.003.
