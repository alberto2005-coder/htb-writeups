---
topic: Exposición parcial de clave RSA
tags: [crypto, rsa, partial-key, factorization, primes]
---

# Exposición parcial de clave RSA

[🐬 English](rsa-partial-key.en.md) | **Español**

## Concepto

Si se filtran bits de `p` o `q`, la relación `n = p*q` permite reconstruir los primos. La búsqueda crece desde el bit menos significativo y se poda con la congruencia módulo `2^k`.

## Cuándo aplica

- Retos que dan `n`, `e`, `c` y una máscara de bits.
- Claves generadas con entropía insuficiente.
- Mensajes que revelan bits de los factores.

## Procedimiento

1. Alinear los bits conocidos desde el LSB.
2. Probar las cuatro combinaciones de bits de `p` y `q` en cada posición.
3. Conservar solo las ramas que cumplen `p*q ≡ n (mod 2^k)`.
4. Validar `p*q == n` al final.
5. Calcular `d` y descifrar.

```python
if ((p + dp) * (q + dq)) % (1 << (k + 1)) == n % (1 << (k + 1)):
    # rama válida
    ...
```

## Variantes

- Bits conocidos desde el MSB.
- Coppersmith cuando se conoce una parte pequeña.
- Ataque de paridad o de bits altos.

## Limitaciones

- Se necesita una fracción suficiente de bits.
- Una máscara mal alineada rompe la poda.
- `p` y `q` deben ser primos válidos.

## Mitigación

- No exponer bits ni valores intermedios.
- Rotar claves tras una fuga.
- Usar generadores con entropía adecuada.

## Detección

- Claves con estructura repetida.
- Publicación de metadatos de generación.
- Retos o APIs que filtran bits.

## Referencias

- <https://en.wikipedia.org/wiki/RSA_(cryptosystem)>
- <https://crypto.stanford.edu/~dabo/papers/RSA-survey.pdf>
- <https://attack.mitre.org/techniques/T1556/>
