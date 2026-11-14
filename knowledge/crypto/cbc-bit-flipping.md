---
topic: Bit flipping en AES-CBC
tags: [crypto, aes, cbc, bit-flipping, malleability, iv]
---

# Bit flipping en AES-CBC

[🌐 English](cbc-bit-flipping.en.md) | **Español**

## Concept

En AES-CBC cada bloque de texto plano se XOR con el bloque de ciphertext anterior antes de cifrarse. Si el atacante conoce el texto plano y puede modificar el ciphertext, cambia un byte del bloque anterior para alterar el byte correspondiente del bloque siguiente.

## Cuándo aplica

- Cifrado CBC sin MAC ni AEAD.
- Cookies, tokens o parámetros que el cliente devuelve cifrados.
- Texto plano con estructura conocida (`user=`, `role=`, `admin`).
- IV o primer bloque controlables.

## Procedimiento

1. Obtener un ciphertext y el texto plano correspondiente.
2. Localizar el byte objetivo en el bloque `P[i]`.
3. Calcular `C[i-1]' = C[i-1] XOR P[i] XOR P[i]'`.
4. Enviar el ciphertext modificado.
5. Asumir que `P[i-1]` queda corrupto.

```text
P[i] = D(C[i]) XOR C[i-1]
C[i-1]' = C[i-1] XOR P[i] XOR P[i]'
```

## Variantes

- Modificar el IV para cambiar solo `P[1]`.
- Convertir `bdmin` en `admin` cambiando un byte.
- Alterar un rol o un identificador en un token.
- Encadenar varios bloques para preservar la estructura.

## Limitaciones

- El bloque anterior al modificado se corrompe.
- Se necesita conocer el texto plano original.
- PKCS#7 puede fallar si el último bloque se altera.
- Un MAC o AEAD invalida el ataque.

## Mitigación y detección

- Usar AES-GCM o encrypt-then-MAC.
- Verificar integridad antes de descifrar.
- No aceptar ciphertexts del cliente sin autenticación.
- Alertar de fallos de padding y de ciphertexts con longitudes o bytes anómalos.

## Referencias

- <https://owasp.org/www-community/attacks/CBC_bit_flipping>
- <https://csrc.nist.gov/publications/detail/sp/800-38a/final>
- <https://cwe.mitre.org/data/definitions/353.html>
- <https://attack.mitre.org/techniques/T1556/>
