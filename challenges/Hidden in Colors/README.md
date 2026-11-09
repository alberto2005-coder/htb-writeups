---
challenge: Hidden in Colors
type: Stego
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [stego, image, lsb, png, zsteg]
---

# Hidden in Colors — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

## Enunciado

Una imagen PNG aparentemente normal contiene información en los bits menos significativos. No hay contraseña ni pista: el reto es extraer la capa oculta.

## Triaje

```bash
file image.png
exiftool image.png
pngcheck -v image.png
binwalk image.png
```

- `exiftool` para metadatos y comentarios.
- `pngcheck` detecta chunks extraños (tEXt, zTXt, iTXt) y errores de CRC.
- `binwalk` señala si hay un ZIP u otro fichero embebido.

## Extracción

1. **LSB con `zsteg`** (el más directo en PNG/BMP):

   ```bash
   zsteg image.png
   zsteg -a image.png       # todas las combinaciones
   ```

2. **`steghide`** si la imagen es JPEG o hay contraseña:

   ```bash
   steghide extract -sf image.jpg
   ```

3. **Bits plano a plano** con Python cuando `zsteg` no da nada:

   ```python
   from PIL import Image
   im = Image.open('image.png').convert('RGB')
   bits = [str(p[i] & 1) for p in im.getdata() for i in range(3)]
   data = bytes(int(''.join(bits[i:i+8]), 2) for i in range(0, len(bits)-7, 8))
   print(data[:200])
   ```

4. **Canales y orden**: probar R, G, B, alfa, orden RGB/BGR y si los bits van en el canal menos significativo o en el más.

## Hallazgos (patrón)

```text
zsteg: b1,rgb,lsb,xy  .. text: "HTB{...}"
```

La cadena aparece al leer el bit 1 del canal RGB en orden xy; si sale ruido, cambia canal u orden.

## Errores típicos

- **`zsteg` no encuentra nada** → la imagen puede ser JPEG (usa `steghide`) o el payload está en el canal alfa.
- **Texto cifrado** → hay contraseña; prueba `steghide` con una wordlist o busca la clave en metadatos.
- **CRC inválido** → la imagen fue modificada a mano; `pngcheck` lo dice y `binwalk` puede extraer el resto.
- **Bits en orden inverso** → invierte la secuencia o lee de derecha a izquierda.

## Lecciones

- El orden de los canales importa tanto como el bit elegido.
- `zsteg -a` es el primer comando, no el último.
- Un PNG con CRC roto es una pista, no un error de descarga.

MITRE: T1027.003 (steganografía).
