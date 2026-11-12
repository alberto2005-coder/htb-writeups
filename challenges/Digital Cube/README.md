---
challenge: Digital Cube
type: Stego
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [stego, qr, binary, images]
---

# Digital Cube — Hack The Box (Challenge)

[🌍 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El archivo entregado contiene datos binarios que, al representarlos con el ancho adecuado, forman un código QR. Ajustando el tamaño del editor o la longitud de línea se obtiene una imagen legible y se decodifica con el móvil.

## Enunciado y superficie

- Stego, Easy, retirado.
- Se entrega un fichero con datos binarios o una imagen corrupta.
- No hay servicio que explotar.

```bash
file digital_cube
xxd digital_cube | head
```

## Reconocimiento

El contenido no es texto legible ni una imagen estándar. Al imprimirlo en un editor con una fuente monoespaciada y un ancho fijo, los caracteres `0`/`1` o los bloques de color empiezan a formar un patrón cuadrado.

```bash
wc -c digital_cube
```

Se prueban anchos de línea que sean múltiplos del tamaño del patrón (por ejemplo 29, 33, 45) hasta que la imagen sea cuadrada.

## Análisis

Si el fichero contiene bytes, se convierte a una imagen de 1 bit por píxel:

```python
from PIL import Image
data = open('digital_cube','rb').read()
# ancho estimado por la raíz cuadrada del número de bits
```

Si contiene texto binario, se ajusta el ancho del editor hasta que el QR sea legible. El QR decodifica la flag.

## Explicación del fallo

La información está codificada visualmente, no cifrada. Cualquiera que descubra la geometría correcta puede reconstruirla sin clave.

## Reproducción local

1. Identificar el tipo de dato.
2. Calcular un ancho cuadrado.
3. Renderizar en blanco y negro.
4. Escanear el QR con `zbarimg` o el móvil.

```bash
zbarimg qr.png
```

## Evidencia

- `file`/`xxd` del archivo.
- Imagen reconstruida.
- Texto decodificado con la flag redactada.

## Lecciones aprendidas

- Los datos visuales dependen del ancho de representación.
- Un QR puede estar “roto” solo por formato.
- Herramientas simples (`zbarimg`) resuelven el paso final.
- La esteganografía visual no es cifrado.

## Mitigación y detección

- No usar imágenes como único canal de secretos.
- Si se requiere, cifrar el contenido antes de codificarlo.
- Validar el formato de imágenes en las subidas.
- En CTF, revisar dimensiones y patrones repetidos.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/stego/digital-cube/>
- <https://github.com/mchehab/zbar>
- <https://en.wikipedia.org/wiki/QR_code>
