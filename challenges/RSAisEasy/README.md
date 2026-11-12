---
challenge: RSAisEasy
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, gcd, shared-prime, modular-arithmetic]
---

# RSAisEasy — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El reto entrega dos módulos RSA y dos ciphertexts cifrados con el mismo exponente. Los módulos no son coprimos: un `gcd` recupera un factor compartido, lo que permite factorizar ambos y descifrar los dos bloques de la flag.

## Enunciado y superficie

- Crypto, Easy, retirado.
- Se entregan `RSAisEasy.py` y `output.txt`.
- `output.txt` contiene `n1`, `n2`, `e`, `c1`, `c2`.

```bash
cat output.txt
```

## Reconocimiento

Se revisa el script: genera dos claves RSA y cifra dos partes de la flag. El exponente es pequeño y los módulos se construyen con primos relacionados.

```python
from math import gcd
p = gcd(n1, n2)
```

## Análisis

Si `p > 1`, ambos módulos comparten un primo. Se calcula:

```python
q1 = n1 // p
q2 = n2 // p
phi1 = (p - 1) * (q1 - 1)
d1 = pow(e, -1, phi1)
m1 = pow(c1, d1, n1)
```

Se repite para `n2` y se concatenan los bytes de `m1` y `m2`. Si el `gcd` directo no basta, se prueba una combinación lineal de los módulos, pero el principio es el mismo: un factor compartido rompe RSA.

## Explicación del fallo

RSA depende de que `n = p*q` sea difícil de factorizar. Si dos módulos comparten un primo, el `gcd` lo revela en tiempo polinómico y ambas claves quedan rotas. El cifrado por bloques no aporta seguridad adicional.

## Reproducción local

1. Leer `n1`, `n2`, `e`, `c1`, `c2`.
2. Calcular `gcd(n1, n2)`.
3. Factorizar y calcular `d` para cada módulo.
4. Descifrar y unir los bloques.

```bash
python3 solve.py
```

## Evidencia

- `gcd` distinto de 1.
- Factorización y descifrado de ambos bloques.
- Flag reconstruida y redactada.

## Lecciones aprendidas

- RSA se rompe si los módulos comparten un factor.
- `gcd` es la primera comprobación ante varios módulos.
- El cifrado por bloques no compensa una clave débil.
- Los scripts del reto suelen revelar la relación entre primos.

## Mitigación y detección

- Generar primos independientes y auditarlos.
- Usar librerías RSA probadas y exponentes estándar.
- Rotar claves si se detecta un factor compartido.
- En CTF, comprobar `gcd` entre todos los módulos.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/rsaiseasy/>
- <https://en.wikipedia.org/wiki/RSA_(cryptosystem)>
- <https://en.wikipedia.org/wiki/Greatest_common_divisor>
