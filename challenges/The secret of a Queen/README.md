---
challenge: The secret of a Queen
type: Misc
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [misc, cipher, substitution, mary-queen-of-scots]
---

# The secret of a Queen — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El reto entrega un texto cifrado con una sustitución monoalfabética asociada a María Estuardo. Se identifican las palabras frecuentes y se resuelve el alfabeto por frecuencia y contexto hasta leer la flag.

## Enunciado y superficie

- Misc, Very Easy, retirado.
- Se entrega un texto cifrado y una pista histórica.
- El alfabeto puede estar mezclado o desplazado.

```bash
cat cipher.txt
wc -c cipher.txt
```

## Reconocimiento

- Contar frecuencias de letras y palabras.
- Buscar patrones de tres letras (`the`, `and`, `que`).
- Revisar si hay números o símbolos que representen letras.
- Identificar el idioma probable.

## Análisis del cifrado

La sustitución mantiene la estructura de las palabras. Se construye una tabla de correspondencias: las letras más frecuentes suelen ser `e`, `a`, `o`; las palabras de una letra, `a`/`y`; las de tres, `the`/`que`. Con contexto se corrigen las ambigüedades.

```python
from collections import Counter
text = open('cipher.txt').read().lower()
print(Counter(c for c in text if c.isalpha()).most_common())
```

## Explicación del fallo

El cifrado clásico no resiste análisis de frecuencia ni texto conocido. La pista histórica reduce el espacio de búsqueda y permite probar alfabetos conocidos.

## Reproducción local

```bash
python3 - <<'PY'
import string
cipher = open('cipher.txt').read()
print(cipher.translate(str.maketrans('ABC...', 'abc...')))
PY
```

## Explotación

Se prueba un alfabeto de sustitución, se corrigen las palabras y se valida con un diccionario. La flag aparece al final o en una frase marcada.

## Evidencia

- Frecuencias y palabras candidatas.
- Tabla de sustitución.
- Texto claro legible.
- Flag redactada.

## Lecciones aprendidas

- La frecuencia es la primera herramienta de criptoanálisis clásico.
- El contexto histórico puede dar el alfabeto.
- Un cifrado monoalfabético no es seguro.

## Mitigaciones y detección

- Usar cifrado moderno autenticado para secretos reales.
- No confiar en sustituciones históricas.
- Documentar el alfabeto y la clave si es un ejercicio.
- Referencias: María Estuardo, sustitución monoalfabética, HTB The secret of a Queen.

## Referencias

- <https://www.hackthebox.com/challenges/The%20secret%20of%20a%20Queen>
- <https://7rocky.github.io/en/ctf/htb-challenges/misc/the-secret-of-a-queen/>
- <https://en.wikipedia.org/wiki/Substitution_cipher>
- <https://attack.mitre.org/techniques/T1140/>
