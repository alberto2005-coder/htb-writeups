---
challenge: Tsayaki
type: Crypto
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [crypto, aes, ctr, nonce-reuse, xor]
---

# Tsayaki — Hack The Box (Challenge)

[🐬 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El servicio cifra mensajes con AES-CTR y reutiliza el nonce en varias sesiones. Al repetir el keystream, dos cifrados permiten recuperar la XOR de los textos claros; el formato conocido de uno de ellos revela el otro y la flag.

## Enunciado y superficie

- Crypto, Hard, retirado.
- Un servicio remoto entrega cifrados de mensajes con un formato fijo.
- El objetivo es descifrar el secreto.

```bash
nc <IP> <PORT>
```

## Reconocimiento

- Cada conexión devuelve un `nonce`, un cifrado y una longitud.
- El servicio permite elegir parte del mensaje.
- El nonce se repite entre consultas.

## Análisis

En CTR, `C = P XOR KS`. Con el mismo nonce y clave, `KS` es idéntico. Para dos cifrados:

```text
C1 XOR C2 = P1 XOR P2
```

Si `P1` es conocido o tiene un formato predecible, se obtiene `P2`. El reto requiere alinear los mensajes y manejar el relleno o la longitud.

```python
from pwn import xor
print(xor(c1, c2))
```

## Explotación

Se recogen dos cifrados con el mismo nonce, se calcula la XOR y se reconstruye el mensaje usando el formato conocido. La flag se valida localmente y no se publica.

```python
known = b'...'
stream = xor(c1, known)
print(xor(c2, stream))
```

## Evidencia

- Nonce repetido en dos respuestas.
- XOR de cifrados con texto legible.
- Flag recuperada y validada.

## Lecciones aprendidas

- CTR es un cifrado de flujo: reutilizar nonce rompe la confidencialidad.
- La XOR de dos textos claros revela patrones y estructuras.
- Un formato conocido convierte la XOR en un descifrado completo.
- El nonce debe ser único por mensaje y clave.

## Mitigaciones y detección

- Usar un nonce aleatorio único o un contador que no se repita.
- Rotar claves y usar AEAD.
- Probar el servicio con mensajes conocidos para detectar repetición.
- Revisar implementaciones que reutilizan el mismo IV.
- Referencias: NIST SP 800-38A, AES-CTR nonce reuse.

## Referencias

- <https://www.hackthebox.com/challenges/Tsayaki>
- <https://csrc.nist.gov/pubs/sp/800/38/a/final>
- <https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR)>
- <https://attack.mitre.org/techniques/T1556/>
