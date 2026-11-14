---
challenge: sekur julius
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, caesar, classical-cipher, bruteforce]
---

# sekur julius — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El texto está cifrado con una variante de César. Probar los 25 desplazamientos y puntuar el resultado con un diccionario recupera el mensaje y la flag.

## Enunciado y superficie

- Crypto, Easy, retirado.
- Se entrega un texto cifrado.
- El nombre alude a Julio César.

## Reconocimiento

```bash
cat ciphertext.txt
python3 - <<'PY'
from collections import Counter
print(Counter(open('ciphertext.txt').read()).most_common(8))
PY
```

- Solo letras y acentos.
- La frecuencia sugiere un desplazamiento fijo.
- No hay clave larga.

## Análisis del código

César aplica `c = (p + k) mod 26`. La variante puede invertir el alfabeto o cambiar el signo del desplazamiento; ambas se cubren probando `k` de 0 a 25 y también el texto invertido.

## Explicación del fallo

La clave vive en un espacio de 26 posibilidades. No hay sal ni difusión: la frecuencia de letras y las palabras comunes permiten identificar el texto claro.

## Reproducción local

```python
def caesar(s, k):
    out = []
    for c in s:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            out.append(chr((ord(c) - base + k) % 26 + base))
        else:
            out.append(c)
    return ''.join(out)

for k in range(26):
    print(k, caesar(data, k))
```

## Explotación

```bash
python solve.py
```

Se elige el desplazamiento que produce palabras legibles. La flag se redacta.

## Evidencia

- Distribución de frecuencias.
- Tabla de 26 candidatos.
- Texto claro legible.

## Lecciones aprendidas

- César no es cifrado moderno.
- El espacio de claves minúsculo permite fuerza bruta.
- La frecuencia y el contexto resuelven ambigüedades.

## Mitigaciones y detección

- Usar AES-GCM o ChaCha20-Poly1305 con claves gestionadas.
- No confundir codificación con cifrado.
- Formarse en criptografía aplicada.

## Referencias

- <https://www.hackthebox.com/challenges/sekur%20julius>
- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/sekur-julius/>
