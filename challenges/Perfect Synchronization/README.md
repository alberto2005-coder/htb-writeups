---
challenge: Perfect Synchronization
category: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, aes, ecb, frequency-analysis]
---

# Perfect Synchronization — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Se cifran con **AES** en modo **ECB** varios mensajes que comparten plantilla. En ECB cada bloque de 16 bytes se cifra igual, sin encadenar: bloques idénticos producen ciphertext idéntico. Con suficientes mensajes se reconstruye el texto por **análisis de frecuencias** a nivel de bloque, sin conocer la clave.

## Evidencia

- `source.py` (cifrado) y `output.txt` (lista de ciphertexts en hexadecimal).

## Método

1. **Confirmar ECB**: mismo bloque de 16 bytes en posiciones equivalentes → mismo ciphertext en varios mensajes.

```python
from collections import Counter
bloques = [c[i:i+16] for c in ct_list for i in range(0, len(c), 16)]
Counter(bloques).most_common(5)
```

2. **Alinear la plantilla**: los mensajes comparten estructura; cada posición de bloque corresponde a un campo (saludo, nombre, despedida).

3. **Frecuencia**: en cada posición, el bloque más repetido es el carácter o palabra más común del idioma/plantilla; probar hipótesis (`' '`, letras frecuentes, palabras del encabezado conocido).

4. **Iterar**: sustituir bloques por su valor y comprobar que el texto resultante es coherente; los mensajes se "sincronizan" y el texto se vuelve legible.

## Tropiezos

- **Padding**: los últimos bloques llevan relleno PKCS#7; ignorarlos al comparar.
- **Codificación**: trabajar en bytes, no en `str`, para no romper los bloques de 16.
- **Confundir CBC**: en CBC el mismo bloque cambia según el IV y el anterior; si no hay repeticiones, no es ECB.

## Lecciones

- ECB filtra estructura: es el modo que nunca hay que usar con datos con patrones.
- La frecuencia de bloques convierte un cifrado "fuerte" en un criptograma resoluble.
- AES-CBC o, mejor, AES-GCM con nonce único evitan el problema.
