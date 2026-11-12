---
challenge: BitsNBytes
type: Stego
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [stego, png, images, stegsolve, bit-planes, base64]
---

# BitsNBytes — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; no jugada en este perfil.
> Sin flag ni bits reales.

## TL;DR

El reto entrega dos PNG que parecen idénticos. Al combinarlos con **StegSolve** en modo **Image Combiner → SUB** aparece una línea vertical de píxeles. Esa línea, leída como bits y agrupada en bytes, produce un Base64 que decodifica la flag.

## 1. Triaje

```bash
file *.png
identify -verbose *.png | grep -E 'Geometry|Colorspace|Depth'
exiftool *.png
pngcheck -v *.png
sha256sum *.png
```

Los dos ficheros tienen el mismo tamaño y dimensiones, pero hashes distintos: hay una diferencia de píxeles. `binwalk` y `zsteg` no muestran nada obvio, así que la vía es la comparación.

## 2. Comparar las imágenes

```bash
compare -metric AE image1.png image2.png diff.png
```

`compare` cuenta píxeles distintos. Para ver dónde están:

```bash
convert image1.png image2.png -compose difference -composite diff.png
```

La diferencia se concentra en una franja. Si el visor la oculta, se amplía:

```bash
convert diff.png -crop 40x512+0+0 +repage -scale 800% diff_zoom.png
```

## 3. StegSolve Image Combiner

En StegSolve:

1. `File` → abrir `image1.png`.
2. `Analyse` → `Image Combiner` → seleccionar `image2.png`.
3. Probar las operaciones: `SUB`, `ADD`, `XOR`, `AND`, `OR`.
4. Guardar el resultado.

Con `SUB`, la zona que era igual se vuelve negra y la línea de píxeles modificados queda visible. Es habitual que la línea esté en la primera columna o en la primera fila; hay que recorrer el resultado.

## 4. De píxeles a bits

Se extrae la línea vertical. Cada píxel se reduce a un bit: negro = `0`, blanco = `1` (o al revés; se prueban ambos). Se agrupan 8 bits en un byte, MSB primero:

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

El resultado empieza con caracteres imprimibles; si no, se invierte el orden de bits o se prueba la primera fila en lugar de la columna.

## 5. Base64

La cadena extraída suele ser Base64:

```bash
echo '<BASE64>' | base64 -d
```

Si el texto parece Base64 pero no decodifica, se comprueba el padding (`=`), se eliminan saltos de línea y se prueban las variantes URL-safe (`-`/`_`).

## 6. Errores típicos

- **`compare` da 0** → se están comparando las imágenes equivocadas o se recomprimieron.
- **La línea no se ve** → probar `ADD`/`XOR` y mirar cada canal por separado.
- **Bits sin sentido** → invertir 0/1, probar LSB del canal rojo o leer la fila en vez de la columna.
- **Base64 inválido** → faltan bits de padding o se incluyó un encabezado.
- **Se pasó la imagen por un editor** → la recompresión destruye la diferencia.

## Lecciones aprendidas

- Dos imágenes “iguales” con hashes distintos siempre merecen un diff.
- StegSolve Image Combiner es más rápido que escribir el diff a mano.
- La información puede estar en una sola fila o columna, no en toda la imagen.
- Un flujo de bits casi nunca es texto: hay que probar orden, polaridad y agrupación.
- Base64 es el siguiente paso natural, no el final.

## Mitigaciones (para retos)

- No recompirmir PNG antes de analizarlos.
- Guardar los originales y trabajar sobre copias.
- Documentar la operación exacta de StegSolve y la orientación de la línea.

MITRE: T1027.003.

## Referencias

- <https://insanitys.medium.com/hack-the-box-retired-stego-challenges-36ccc5f3dab1>
- <https://github.com/Giotino/stegsolve>
- <https://imagemagick.org/script/compare.php>
