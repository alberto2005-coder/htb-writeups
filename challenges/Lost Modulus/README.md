---
challenge: Lost Modulus
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, cube-root, gmpy2]
---

# Lost Modulus — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin flag real.

## TL;DR

El script cifra la flag con RSA y `e = 3`, pero no entrega el módulo `n`. Como el mensaje es corto, `m^3 < n` y el cifrado no llega a reducirse módulo `n`; basta con calcular la raíz cúbica exacta del criptograma y convertirla a bytes.

## Enunciado y superficie

- Crypto, Very Easy, retirado.
- Se entrega un script de cifrado y el criptograma en hexadecimal.
- El módulo `n` no se publica: de ahí el nombre.

```bash
file challenge.py
python3 challenge.py
```

## Reconocimiento

El código genera dos primos de 512 bits, usa `e = 3` y calcula `c = m^3 mod n`. No imprime `n`. El criptograma es un entero grande.

```python
ct = int(ciphertext, 16)
```

## Análisis del código

La vulnerabilidad es el exponente bajo combinado con un mensaje corto. Si `m^3 < n`, la operación `mod n` no altera el resultado y `c` es un cubo perfecto. La raíz cúbica entera devuelve el mensaje sin necesitar `p`, `q` ni `d`.

```text
c = m^3
m = integer_cube_root(c)
```

## Explicación del fallo

RSA sin relleno (textbook RSA) es determinista y maleable. Con `e = 3` y un mensaje de pocos bytes, el atacante puede comprobar si `c` es un cubo perfecto. Si lo es, la raíz exacta revela `m`.

## Reproducción local

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install gmpy2
```

```python
import gmpy2
from Crypto.Util.number import long_to_bytes

c = int(open('ciphertext.txt').read().strip(), 16)
m, exact = gmpy2.iroot(c, 3)
if exact:
    print(long_to_bytes(int(m)))
```

`iroot` devuelve `(raíz, True)` cuando el cubo es exacto. Si `exact` es falso, el mensaje es mayor que `n` y este ataque no aplica.

## Explotación

No hay servidor. La explotación es matemática: calcular la raíz y decodificar. La salida correcta tiene el formato de flag de HTB; se verifica en la plataforma y se redacta.

## Evidencia

- Script con `e = 3` y ausencia de `n`.
- `gmpy2.iroot(c, 3)` con `exact = True`.
- Bytes decodificados con la flag redactada.

## Lecciones aprendidas

- RSA textbook con exponente bajo y mensaje corto se rompe sin factorizar.
- `e = 3` no es inseguro por sí solo; lo es la combinación sin relleno.
- La comprobación de cubo perfecto es barata.
- `gmpy2.iroot` es la herramienta adecuada para raíces enteras grandes.

## Mitigaciones y detección

- Usar RSA-OAEP o un esquema híbrido con relleno aleatorio.
- No usar `e = 3` con mensajes cortos sin padding.
- Validar longitudes y rechazar criptogramas que sean potencias perfectas.
- En CTF, documentar el tamaño del mensaje y el exponente.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/lost-modulus/>
- <https://en.wikipedia.org/wiki/RSA_(cryptosystem)#Attacks_against_plain_RSA>
- <https://pypi.org/project/gmpy2/>
