---
challenge: I know Mag1k
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, des, cbc, padding-oracle, web]
---

# I know Mag1k — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin cookie ni flag reales.

## TL;DR

La cookie de sesión está cifrada y el servidor devuelve 500 si el padding es inválido. El bloque es de 8 bytes, así que se trata de DES-CBC con PKCS#7. Un ataque de padding oracle permite descifrar la cookie y, después, cifrar un JSON con `"role":"admin"` para escalar.

## Enunciado y superficie

- Crypto/Web, Easy, retirado.
- Aplicación con login y una cookie `iknowmag1k`.
- El servidor responde distinto ante padding válido e inválido.

```bash
curl -i http://<IP>/profile.php
```

## Reconocimiento

La cookie es base64 y su longitud no es múltiplo de 16; sí de 8. Eso descarta AES y apunta a DES-CBC.

```text
cookie = base64(IV || ciphertext)
block_size = 8
```

Se comprueba que añadir 8 caracteres al usuario produce 16 bytes cifrados adicionales.

## Análisis del código

El servidor descifra la cookie, quita el padding PKCS#7 y muestra el dashboard si el JSON es válido. Un padding incorrecto produce `500 Internal Server Error`; un padding correcto produce `200`. Esa diferencia es el oráculo.

## Explicación del fallo

CBC es maleable: modificando el bloque anterior se controla el plaintext del bloque siguiente. El oráculo de padding permite recuperar byte a byte el valor descifrado y, con él, reutilizar la primitiva para cifrar un JSON arbitrario.

## Reproducción local

Se implementa el oráculo con `requests`:

```python
def oracle(cookie):
    r = requests.get(f'{url}/profile.php', cookies={
        'PHPSESSID': phpsessid,
        'iknowmag1k': cookie
    })
    return r.status_code != 500
```

Para cada bloque se prueba el último byte hasta obtener padding `0x01`, se calcula el byte intermedio y se repite con `0x02`, `0x03`, etc.

## Explotación

Se descifra la cookie original y se construye el JSON objetivo:

```json
{"user":"<USER>","role":"admin"}
```

Se cifra con la misma primitiva (el oráculo también sirve para cifrar) y se envía. El servidor muestra el panel de administrador con la flag.

## Evidencia

- Diferencia 500/200 y longitud de bloque 8.
- Script de padding oracle con la cookie redactada.
- Panel de admin con la flag redactada.

## Lecciones aprendidas

- El tamaño del bloque identifica el cifrado.
- Un error distinto por padding inválido es un oráculo.
- CBC sin autenticación permite descifrar y cifrar.
- La misma primitiva sirve para forjar el JSON de admin.

## Mitigaciones y detección

- Usar AEAD (AES-GCM, ChaCha20-Poly1305) y autenticar la cookie.
- No revelar errores de padding; responder siempre igual.
- Firmar la sesión en servidor y no confiar en el rol del cliente.
- Detección: muchas peticiones con cookies alteradas y respuestas 500.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/i-know-mag1k/>
- <https://owasp.org/www-community/attacks/Padding_Oracle_Attack>
- <https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#CBC>
