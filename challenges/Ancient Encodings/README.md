---
challenge: Ancient Encodings
category: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, base64, hex, encodings]
type: Crypto
---


# Ancient Encodings — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

`source.py` muestra el "cifrado": `hex(bytes_to_long(b64encode(FLAG)))`. No hay clave ni criptografía real: es **base64** y luego **hexadecimal**. Se deshace en dos pasos, en orden inverso.

## Enunciado y superficie

- Categoría Crypto; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

`source.py` muestra el "cifrado": `hex(bytes_to_long(b64encode(FLAG)))`. No hay clave ni criptografía real: es **base64** y luego **hexadecimal**. Se deshace en dos pasos, en orden inverso.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `source.py` y `output.txt` (un entero hexadecimal enorme).

## Lecciones aprendidas

- **`6` inicial**: `bytes_to_long` mete un byte `0x06` delante; `int(data, 16)` lo convierte y `long_to_bytes` lo vuelve a dejar como byte, por eso el base64 decodifica bien aunque sobre un byte.
- **Quitar el `0x`**: si se pasa el prefijo a `int(..., 16)` con base 16 explícita, Python lo acepta; si se hace `bytes.fromhex` con `0x`, falla.
- **Saltos de línea** en `output.txt`: usar `strip()`.

- Base64 y hex son **codificaciones**, no cifrado: reversibles sin clave.
- Identificar la capa por el alfabeto (`A-Za-z0-9+/=` frente a `0-9a-f`) ahorra tiempo.
- En CTF, `source.py` es la especificación: se lee antes de probar herramientas.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)
- [block-ciphers](../../knowledge/crypto/block-ciphers.md)

## Método

1. **Leer el cifrado**:

```python
from Crypto.Util.number import bytes_to_long
from base64 import b64encode

def encode(message):
    return hex(bytes_to_long(b64encode(message)))
```

2. **Deshacer**: hex → bytes → base64 → texto.

```python
from Crypto.Util.number import long_to_bytes
from base64 import b64decode

data = open("output.txt").read().strip()
print(b64decode(long_to_bytes(int(data, 16))).decode())
```

3. **Equivalente en CyberChef**: `From Hex` → `From Base64` → `To Text`.
