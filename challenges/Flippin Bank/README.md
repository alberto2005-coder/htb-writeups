---
challenge: Flippin Bank
type: Crypto
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [crypto, aes, cbc, bit-flipping, known-plaintext, length-extension]
---

# Flippin Bank — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El servidor cifra en AES-CBC un mensaje `logged_username=<user>&password=<pass>` y devuelve el ciphertext. Si se envía un ciphertext cuyo descifrado contiene `admin&password=<PASSWORD>`, entrega la flag. Modificando un byte del primer bloque se altera el bloque de texto plano siguiente y se convierte `bdmin` en `admin`.

## Enunciado y superficie

- Crypto, Medium, retirado.
- Se entrega el código Python del servidor y una instancia remota.
- El servidor escucha en 1337.

```bash
nc <IP> 1337
```

## Reconocimiento

El código muestra:

- AES-CBC con clave e IV aleatorios por proceso.
- PKCS#7.
- Un mensaje construido con el usuario y la contraseña.
- Una comprobación que prohíbe la subcadena `admin&password=<PASSWORD>` en el mensaje original.

```python
msg = 'logged_username=' + user + '&password=' + passwd
assert 'admin&password=<PASSWORD>' not in msg
```

## Análisis del código

El cifrado no incluye autenticación. En CBC, cada bloque de texto plano se XOR con el bloque de ciphertext anterior antes de cifrarse. Cambiar un byte de `C[i-1]` cambia el byte correspondiente de `P[i]` y corrompe `P[i-1]`.

```text
P1 = D(C1) XOR IV
P2 = D(C2) XOR C1
```

## Explicación del fallo

Se elige un usuario `bdmin` y una contraseña que empiece por `g0ld3n_b0y`. El mensaje original contiene `bdmin&password=g...`, que no coincide con la cadena prohibida. Al cambiar el primer byte de `C1`, el primer byte de `P2` pasa de `b` a `a`, y el segundo bloque empieza por `admin&password=g...`.

## Reproducción local

```bash
python3 -m venv venv
. venv/bin/activate
pip install pycryptodome pwntools
python server.py
```

- El servidor local usa una clave y un IV aleatorios.
- Se prueba el script contra localhost antes de la instancia.

## Explotación

```python
from pwn import remote

io = remote("<IP>", 1337)
io.sendlineafter(b"username: ", b"bdmin")
io.sendlineafter(b"password: ", b"g0ld3n_b0y")

io.recvuntil(b"Leaked ciphertext: ")
ct = bytearray.fromhex(io.recvline().decode())
ct[0] ^= ord("b") ^ ord("a")
io.sendlineafter(b"enter ciphertext: ", ct.hex().encode())
print(io.recvall().decode())
```

La respuesta contiene la flag; se redacta.

## Evidencia

- Ciphertext original y modificado, con el byte señalado.
- Salida del servidor que confirma el login.
- Flag redactada.

## Lecciones aprendidas

- CBC sin MAC es malleable.
- Un byte controlado en el bloque anterior cambia el bloque siguiente.
- Las comprobaciones sobre el texto plano original no protegen el ciphertext.

## Mitigaciones y detección

- Usar AES-GCM o cifrar-y-autenticar con HMAC.
- Verificar la integridad antes de descifrar y rechazar ciphertexts alterados.
- No aceptar ciphertexts arbitrarios del cliente.
- Alertar de fallos de padding, longitudes anómalas y múltiples intentos de descifrado.

## Referencias

- <https://www.hackthebox.com/challenges/Flippin%20Bank>
- <https://csrc.nist.gov/publications/detail/sp/800-38a/final>
- <https://owasp.org/www-community/attacks/CBC_bit_flipping>
- <https://attack.mitre.org/techniques/T1556/>
