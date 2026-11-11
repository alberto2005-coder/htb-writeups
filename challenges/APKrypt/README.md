---
challenge: APKrypt
category: Challenge
type: Mobile
os: Android
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, apk, smali, aes, hardcoded-key, jadx]
---

# APKrypt — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

APK de Android que pide un código VIP y, si el MD5 coincide con un valor escrito en el código, descifra un blob base64. La clave AES también está en el binario y el modo es ECB, así que no hay nada que romper: se descompila, se lee la clave, se descifra el blob y se obtiene la flag.

## Enunciado y superficie

- Categoría **Mobile**, dificultad **Easy**.
- Entrega `APKrypt.apk` y un `README` que pide instalarlo en API 29 o anterior.
- No hace falta emulador: el análisis es estático.

```bash
file APKrypt.apk
apktool decode APKrypt.apk -o apkrypt_src
```

## Reconocimiento

```bash
grep -ril "vip\|aes\|md5" apkrypt_src/smali | head
```

El `AndroidManifest.xml` declara una sola actividad. En `smali/com/example/apkrypt/MainActivity.smali` aparece la comparación del hash y la llamada a `generateKey()`, que devuelve una clave fija.

## Análisis del código

```bash
d2j-smali apkrypt_src/smali/com/example/apkrypt/*.smali -o out.dex
d2j-dex2jar out.dex -o apkrypt.jar
jd-gui apkrypt.jar
```

En el decompilado:

- El botón calcula `MD5(código)` y lo compara con `735c3628699822c4c1c09219f317a8e9`.
- Si coincide, descifra la cadena base64 `k+RLD5J86JRYnluaZLF3Zs/yJrVdVfGo1CQy5k0+tCZDJZTozBWPn2lExQYDHH1l`.
- `generateKey()` no genera nada: devuelve `new SecretKeySpec("Dgu8Trf6Ge4Ki9Lb".getBytes(), "AES")`.
- El cifrado se instancia como `AES/ECB/PKCS5Padding`, sin IV.

## Explicación del fallo

Dos decisiones convierten el reto en un ejercicio de lectura: la clave está en el código y el modo ECB no usa IV. El "código VIP" solo controla si se entra en la rama de descifrado; no protege el secreto.

```text
clave  = Dgu8Trf6Ge4Ki9Lb  (16 bytes, AES-128)
modo   = ECB, relleno PKCS#5/7
datos  = base64 de 64 bytes -> 3 bloques + relleno
```

## Reproducción local

```python
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

ct = b64decode("k+RLD5J86JRYnluaZLF3Zs/yJrVdVfGo1CQy5k0+tCZDJZTozBWPn2lExQYDHH1l")
pt = AES.new(b"Dgu8Trf6Ge4Ki9Lb", AES.MODE_ECB).decrypt(ct)
print(unpad(pt, 16).decode())
```

## Explotación

1. `apktool d` y localizar `MainActivity`.
2. Extraer clave y blob con `grep` o con jadx.
3. Descifrar con el script anterior.
4. Introducir el resultado donde el reto lo pida.

No hace falta calcular el MD5: el código solo compara, no deriva la clave del código.

## Evidencia

- Captura del decompilado con la clave y el blob recortados.
- Salida del script con la flag parcialmente oculta.

## Lecciones aprendidas

- Una comprobación de integridad en el cliente no protege un secreto: la clave está al lado.
- ECB revela patrones y no aporta confidencialidad real; aquí además la clave es fija.
- `apktool` + jadx bastan para apps sin ofuscación; no siempre hace falta Frida.
- El "código VIP" era una pista, no la protección.

## Mitigaciones y detección

- No incrustar claves en el APK; usar el Keystore y derivar claves por dispositivo.
- Emplear AES-GCM con nonce aleatorio en lugar de ECB.
- Ofuscar y comprobar la integridad en el servidor, no en el cliente.
- Detección: APKs con cadenas base64 largas y constantes de 16 bytes, uso de `SecretKeySpec` con literales y ausencia de `SecureRandom`.
- Referencias: OWASP MASVS-CRYPTO, CWE-321 (hard-coded key).

## Referencias

- <https://www.hackthebox.com/challenges/apkrypt>
- <https://bryanmcnulty.com/posts/htb-apkrypt>
- <https://dua2z3rr.github.io/posts/APKrypt-Walkthrough>
- <https://mas.owasp.org/MASVS/05-MASVS-CRYPTO/>
