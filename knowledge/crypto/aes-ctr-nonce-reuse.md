---
topic: Reutilización de nonce en AES-CTR
tags: [crypto, aes, ctr, nonce, xor, keystream]
---

# Reutilización de nonce en AES-CTR

[🐬 English](aes-ctr-nonce-reuse.en.md) | **Español**

## Concepto

AES-CTR genera un keystream a partir de clave y nonce. Si el nonce se repite, el mismo keystream cifra varios mensajes; la XOR de dos cifrados elimina el keystream y revela la XOR de los textos claros.

## Cuándo aplica

- Servicios que devuelven `nonce` y cifrado.
- Implementaciones que usan un IV fijo.
- Retos con mensajes de formato conocido.

## Procedimiento

1. Recoger dos cifrados con el mismo nonce.
2. Calcular `C1 XOR C2`.
3. Usar el formato o un texto conocido para separar `P1 XOR P2`.
4. Recuperar el keystream y descifrar el resto.
5. Validar la flag.

```python
from pwn import xor
x = xor(c1, c2)
stream = xor(c1, known_plaintext)
plaintext = xor(c2, stream)
```

## Variantes

- Nonce predecible en lugar de repetido.
- Cifrado de flujo con contador que se reinicia.
- Ataque de diccionario sobre mensajes cortos.

## Limitaciones

- Nonces únicos impiden la XOR directa.
- Longitudes distintas requieren alinear.
- El formato debe ser suficientemente conocido.

## Mitigación

- Nonce aleatorio único por mensaje y clave.
- Contador que no se repita; rotación de claves.
- Usar AEAD (GCM/ChaCha20-Poly1305).

## Detección

- Nonces repetidos en respuestas.
- Mismo prefijo de cifrado.
- Pruebas con mensajes controlados.

## Referencias

- <https://csrc.nist.gov/pubs/sp/800/38/a/final>
- <https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR)>
- <https://attack.mitre.org/techniques/T1556/>
