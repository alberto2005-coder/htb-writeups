# Esteganografía en imágenes y audio

[🇬🇧 English](images-audio.en.md) | **Español**

Checklist para retos de Stego: qué mirar en una imagen o un audio antes de asumir que no hay nada.

## 1. Imágenes — triaje

```bash
file image.*; exiftool image.*
pngcheck -v image.png
binwalk -e image.png
identify -verbose image.png | head -40
```

- Comentarios EXIF (`Comment`, `UserComment`) y `tEXt`/`zTXt`.
- `binwalk` para un ZIP/PDF embebido tras el `IEND`.
- Diferencias de tamaño respecto al original si el reto lo da.

## 2. LSB y planos de bits

```bash
zsteg image.png
zsteg -a image.png
```

`zsteg` informa combinación (`b1,rgb,lsb,xy`), longitud y tipo. Si no hay resultado:

- Prueba cada canal por separado (`b1,r`, `b1,g`, `b1,b`, `b1,a`).
- Prueba MSB (`b8`) y órdenes `xy`/`yx`.
- Extrae a mano con Pillow y busca cabeceras (`PK`, `%PDF`, `\x89PNG`) en el flujo de bits.

## 3. JPEG y contraseñas

```bash
steghide info image.jpg
steghide extract -sf image.jpg -p <pass>
stegseek image.jpg rockyou.txt
```

`stegseek` rompe `steghide` con diccionario en segundos. Si el reto menciona una frase del enunciado, pruébala como contraseña.

## 4. Comparar dos imágenes

Cuando hay original y modificada:

```bash
compare -metric AE original.png modificada.png diff.png
python3 - <<'PY'
from PIL import Image, ImageChops
a = Image.open('original.png').convert('RGB')
b = Image.open('modificada.png').convert('RGB')
ImageChops.difference(a, b).save('diff.png')
PY
```

Ampliar el diff y mirar los píxeles con diferencia distinta de cero.

## 5. Audio

```bash
soxi audio.wav
sox audio.wav -n spectrogram -o spec.png     # o Sonic Visualiser
```

- **Espectrograma**: texto dibujado en frecuencias altas, muy común.
- **DTMF**: tonos de marcación → `multimon-ng -t wav -a DTMF audio.wav`.
- **Morse (CW)**: `multimon-ng -t wav -a MORSE_CW audio.wav` (el demodulador se llama `MORSE_CW`, no `MORSE`).
- **LSB de muestras**: script propio con `soundfile`/`wave`; no hay herramienta estándar.
- **Metadatos**: `exiftool`, `ffprobe -show_format`.

## 6. Qué no hacer

- No pasar la imagen por redes sociales: recomprimen y destruyen el LSB.
- No asumir que `steghide` es la única herramienta; también hay `outguess`, `openstego`, `stegolsb`.
- No ignorar el canal alfa: es el escondite más habitual tras RGB.

## Lecciones

- `zsteg -a` primero, siempre.
- Un diff entre dos versiones de la imagen resuelve más retos que cualquier herramienta.
- En audio, el espectrograma es la primera parada, no la última.

MITRE: T1027.003.
