---
challenge: Cryptohorrific
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, ios, aes, plist, cccrypt, hopper]
---

# Cryptohorrific — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

**No es Android: es una app iOS.** Se entrega un bundle `.app` con un binario Mach-O y un `challenge.plist` que guarda un blob base64. En `ViewController` hay una llamada a `CCCrypt` con la clave y el IV en claro; reproduciendo ese AES fuera de la app sale la flag.

## Enunciado y superficie

«Secure coding is the keystone of the application security!» Categoría Mobile. Se entrega el bundle de una aplicación iOS (`hackthebox.app`) con su `Info.plist`, recursos y el ejecutable Mach-O de 64 bits.

## Reconocimiento

```bash
unzip -l Cryptohorrific.zip
file hackthebox.app/hackthebox          # Mach-O 64-bit x86_64
plistutil -i hackthebox.app/challenge.plist -o challenge.xml
cat challenge.xml
```

El plist tiene tres campos (`title`, `id`, `flag`); `flag` es un base64 largo. `plistutil` (o `plistlib` de Python) lo convierte a XML legible.

## Análisis del código

```bash
strings -a hackthebox.app/hackthebox | grep -iE 'key|iv|CCCrypt|AES'
```

El binario es Mach-O y llama a **`CCCrypt`** (CommonCrypto). En Hopper/IDA, siguiendo `-[ViewController viewDidLoad]`, aparecen la clave y el IV como literales:

```text
key = !A%D*G-KaPdSgVkY
iv  = QfTjWnZq4t7w!z%C
```

## Explicación del fallo

La clave está **en el cliente**. Cualquiera con el bundle la extrae en minutos, así que el cifrado solo aporta ofuscación. El modo efectivo es AES-128-**ECB**, sin autenticación: el IV está en el código pero no protege nada.

## Reproducción local

```python
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

ct = base64.b64decode("<blob del plist>")
k = b"!A%D*G-KaPdSgVkY"
print(unpad(AES.new(k, AES.MODE_ECB).decrypt(ct), 16).decode())
```

Equivalente con OpenSSL:

```bash
echo "<blob>" | base64 -d | \
  openssl enc -d -aes-128-ecb -nopad -K "$(printf '%s' '!A%D*G-KaPdSgVkY' | xxd -p)"
```

## Explotación

1. Extraer el bundle y convertir el plist a XML.
2. Identificar el blob base64 del campo `flag`.
3. Localizar `CCCrypt` y sus argumentos en el Mach-O.
4. Descifrar en local con la clave (en ECB el IV no cambia el resultado).

## Evidencia

- `challenge.plist` con el blob base64 (redactado).
- `strings`/Hopper mostrando `CCCrypt` y los literales de clave.
- Texto descifrado con formato `HTB{...}`.

## Lecciones aprendidas

- **Es iOS, no Android**: si el ZIP trae `Info.plist` y un Mach-O, `jadx` no sirve; hacen falta Hopper/IDA/radare2 y `plistutil`.
- **`CCCrypt` es el punto de entrada**: en apps Apple casi todo el cifrado simétrico pasa por ahí.
- **ECB no usa el IV**: si el resultado no cuadra probando CBC, comprobar el modo antes de rehacer la clave.
- Una clave en el binario no es un secreto, solo una molestia.

## Mitigaciones y detección

- No cifrar secretos con claves embebidas: el binario es público por definición.
- Si hace falta cifrado en cliente, clave derivada por usuario, verificación en servidor y AES-GCM con nonce; nunca ECB.
- Revisión: buscar `CCCrypt`/`kCCAlgorithmAES` con claves literales en el binario.

## Referencias

- [MITRE T1409](https://attack.mitre.org/techniques/T1409/)
- [MITRE T1521](https://attack.mitre.org/techniques/T1521/)
- [apk-analysis](../../knowledge/mobile/apk-analysis.md)
