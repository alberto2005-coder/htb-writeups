---
topic: Padding oracle en CBC
tags: [crypto, cbc, pkcs7, padding-oracle, aes, des]
---

# Padding oracle en CBC

[🇬🇧 English](padding-oracle.en.md) | **Español**

## Concepto

En CBC, cada bloque de plaintext se XOR con el bloque de ciphertext anterior. Si el servidor revela si el padding PKCS#7 es válido, un atacante puede modificar el bloque anterior y observar la respuesta para recuperar el plaintext byte a byte. La misma primitiva permite cifrar un mensaje arbitrario.

## Cuándo aplica

- Cifrado CBC con PKCS#7 y sin autenticación (sin MAC/AEAD).
- El servidor distingue padding inválido de datos inválidos (código, mensaje o tiempo).
- El atacante controla el IV y el ciphertext (cookie, token, parámetro).
- Se conoce el tamaño de bloque (8 para DES/3DES, 16 para AES).

## Requisitos y condiciones

1. Ciphertext e IV accesibles.
2. Oráculo observable (200 vs 500, redirección, tiempo).
3. Capacidad de enviar muchos valores sin bloqueo.
4. Padding PKCS#7 estándar.

## Procedimiento

Para el último bloque, se modifica el penúltimo byte a byte hasta que el padding sea `0x01`. El byte intermedio es `b ^ 0x01`; el plaintext es `prev_block[-1] ^ intermedio`. Se repite con `0x02`, `0x03`, etc.

```python
def oracle(cookie):
    r = requests.get(url, cookies={'session': cookie})
    return r.status_code != 500
```

```python
for b in range(256):
    forged = prev[:-1] + bytes([b])
    if oracle(base64.b64encode(forged + ct)):
        inter = b ^ 0x01
        plain = prev[-1] ^ inter
        break
```

Para cifrar, se elige el bloque objetivo y se calcula el bloque anterior como `D(C) ^ P`.

## Variantes

- **POODLE**: padding oracle en SSL 3.0 con CBC.
- **Lucky13**: diferencia de tiempo en TLS CBC.
- **Cookie/token**: el oráculo es una cookie de sesión o un token cifrado.
- **Padding oracle + bit flipping**: si no hay oráculo, a veces basta con modificar el IV.

## Limitaciones

- AEAD (AES-GCM, ChaCha20-Poly1305) no es vulnerable a este ataque.
- Un MAC o una firma sobre el ciphertext lo bloquea.
- Los WAF y el rate limiting dificultan la explotación.
- El padding puede ser distinto de PKCS#7 (ZeroPadding, ISO 10126).

## Mitigación

- Usar AEAD y autenticar el ciphertext.
- No revelar errores de padding; responder siempre igual.
- Firmar cookies/tokens en servidor.
- Rotar claves si se detecta explotación.

## Detección

- Ráfagas de peticiones con cookies alteradas y respuestas 500.
- Diferencias de tiempo entre padding válido e inválido.
- Aumento de errores 400/500 en endpoints con tokens cifrados.
- WAF: reglas para payloads base64 alterados repetidamente.

MITRE ATT&CK: T1552 (Unsecured Credentials), T1140 (Deobfuscate/Decode Files or Information).

## Referencias

- <https://owasp.org/www-community/attacks/Padding_Oracle_Attack>
- <https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#CBC>
- <https://www.openssl.org/docs/man3.0/man7/EVP_CIPHER-AES.html>
