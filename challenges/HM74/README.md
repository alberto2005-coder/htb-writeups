---
challenge: HM74
type: Hardware
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [hardware, hamming-code, error-correction, encoding]
---

# HM74 — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El reto entrega una secuencia de bits con ruido. Cada bloque de siete bits es un código Hamming(7,4): cuatro datos y tres paridades. Corrigiendo el bit erróneo de cada bloque y concatenando los datos se recupera el mensaje.

## Enunciado y superficie

- Hardware, Very Easy, retirado.
- Se entrega un archivo de texto con bits.
- El nombre `HM74` apunta a Hamming(7,4).

## Reconocimiento

```bash
file hm74.txt
head -3 hm74.txt
wc -c hm74.txt
```

- Solo bits y separadores.
- La longitud es múltiplo de 7 si se ignoran espacios.
- No hay binario que ejecutar.

## Análisis del código

Hamming(7,4) codifica 4 bits de datos en 7 posiciones. Las posiciones 1, 2 y 4 son paridad; 3, 5, 6 y 7 son datos. El síndrome formado por las tres comprobaciones indica la posición del bit erróneo (0 si no hay error).

## Explicación del fallo

No es una vulnerabilidad: es un ejercicio de corrección de errores. El "ruido" cambia un bit por bloque; sin corregirlo, los datos no forman ASCII legible.

## Reproducción local

```python
blocks = [b for b in bits if len(b) == 7]
for b in blocks:
    p1 = int(b[0]) ^ int(b[2]) ^ int(b[4]) ^ int(b[6])
    p2 = int(b[1]) ^ int(b[2]) ^ int(b[5]) ^ int(b[6])
    p4 = int(b[3]) ^ int(b[4]) ^ int(b[5]) ^ int(b[6])
    syndrome = p1 + 2*p2 + 4*p4
    if syndrome:
        b = flip(b, syndrome - 1)
    data += b[2] + b[4] + b[5] + b[6]
```

Se agrupan los bits de datos en bytes y se decodifica ASCII.

## Explotación

```bash
python solve.py hm74.txt
```

El script imprime el mensaje; la flag se redacta.

## Evidencia

- Distribución de longitudes de bloque.
- Síndromes distintos de cero y posiciones corregidas.
- Texto ASCII resultante.

## Lecciones aprendidas

- Los códigos de bloque permiten detectar y corregir errores.
- Un síndrome no es un hash: identifica una posición.
- Conviene validar la paridad antes de interpretar los datos.

## Mitigaciones y detección

- En sistemas reales, usar CRC o ECC adecuados al medio.
- No confundir corrección de errores con integridad criptográfica.
- Documentar el esquema de codificación.

## Referencias

- <https://www.hackthebox.com/challenges/HM74>
- <https://en.wikipedia.org/wiki/Hamming(7,4)>
