---
topic: Cifrado casero y ataque con texto conocido
tags: [crypto, custom-cipher, known-plaintext, brute-force]
---

# Cifrado casero y ataque con texto conocido

[🌐 English](custom-cipher-known-plaintext.en.md) | **Español**

## Concepto

Un cifrado propio suele combinar sumas, XOR o rotaciones con una clave corta. Si se conoce parte del texto plano o el formato de salida, se puede invertir la transformación y reducir el espacio de claves hasta recuperar la frase de paso.

## Cuándo aplica

- Hay un script de cifrado y un texto cifrado.
- Se conoce o se adivina parte del contenido.
- La clave es una contraseña de diccionario.

## Procedimiento

1. Leer el script y expresar el cifrado en una función inversa.
2. Probar con un texto conocido para validar la implementación.
3. Iterar un diccionario y comprobar si el resultado es imprimible.
4. Usar la frase encontrada en el siguiente sistema.

```python
def decrypt(data, key):
    out = bytearray()
    for i, b in enumerate(data):
        out.append((b - key[i % len(key)]) % 256)
    return bytes(out)

for key in open("rockyou.txt", "rb").read().splitlines():
    p = decrypt(ciphertext, key)
    if p.startswith(b"<KNOWN>"):
        print(key, p)
        break
```

## Variantes

- XOR con clave repetida y análisis de frecuencia.
- Cifrado por bloques con IV fijo.
- Ofuscación con Base64 y una resta constante.

## Limitaciones

- Sin texto conocido el espacio puede ser grande.
- Una clave aleatoria larga no es atacable por diccionario.
- El formato de salida debe ser reconocible.

## Mitigación y detección

- No diseñar cifrados propios; usar AES-GCM o ChaCha20-Poly1305.
- Derivar claves con Argon2 o PBKDF2 y una sal única.
- No reutilizar contraseñas entre volúmenes y servicios.

## Referencias

- <https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html>
- <https://en.wikipedia.org/wiki/Known-plaintext_attack>
- <https://attack.mitre.org/techniques/T1552/>
