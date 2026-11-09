---
title: XOR y cadenas de codificaciones (CTF y forense)
tags: [crypto, xor, base64, hex, forensics]
---

# XOR y cadenas de codificaciones

[🇬🇧 English](xor-and-encodings.en.md) | **Español**

## 1. Cuándo mirar aquí

Retos de crypto muy fáciles y artefactos de forense comparten el mismo patrón: un blob que «no es nada» hasta que se aplica XOR con una clave trivial o se encadenan dos codificaciones. Antes de escribir un script, identifica el fichero:

```bash
file blob.bin
xxd blob.bin | head
```

Si la entropía es alta pero hay estructura repetida, sospecha XOR. Si empieza por `====` o solo tiene `A-Za-z0-9+/`, es base64.

## 2. XOR de un byte

Fuerza bruta de 256 claves y puntúa el resultado por imprimibilidad:

```python
data = open('blob.bin','rb').read()
for k in range(256):
    out = bytes(b ^ k for b in data)
    if out.count(b'flag{') or out.startswith(b'PK\x03\x04') or out.startswith(b'\x89PNG'):
        print(k, out[:80]); open(f'x_{k}.bin','wb').write(out)
```

La pista está en los **magic bytes**: `PK\x03\x04` (ZIP), `%PDF`, `\xd0\xcf\x11\xe0` (OLE), `\x89PNG`. En un ZIP, XOR con `0xFF` sobre el fichero entero suele ser el caso de «Took the Byte»: el archivo se abre después de aplicarlo.

## 3. XOR con clave repetida

Si conoces el prefijo (`flag{`, `picoCTF{`) recuperas la clave:

```python
ct = open('cipher.bin','rb').read()
known = b'flag{'
key = bytes(c ^ p for c, p in zip(ct, known))
print(key)   # repite el patrón hasta la longitud real
```

Con clave más corta que el mensaje, repite el patrón y descifra:

```python
key = b'<clave>'
pt = bytes(c ^ key[i % len(key)] for i, c in enumerate(ct))
print(pt)
```

Sin prefijo conocido: prueba longitudes de 1 a 32 y quédate con la que dé texto legible (frecuencia de espacios y letras). `xortool` automatiza eso:

```bash
xortool cipher.bin -c 20 -l 8
```

## 4. Codificaciones encadenadas

Orden típico: **hex → base64 → texto**, o al revés. Detecta por alfabeto:

```python
import base64, binascii, string

def decode(s):
    s = s.strip()
    for name, fn in [('hex', binascii.unhexlify), ('b64', base64.b64decode)]:
        try:
            out = fn(s)
            if all(chr(b) in string.printable for b in out):
                print(name, out[:100]); return out
        except Exception:
            pass
```

Recursivo hasta que no cambie. CyberChef con la operación *Magic* hace lo mismo a ojo cuando hay pocas capas.

## 5. Errores típicos

- **`binascii.Error: Invalid base64`** → hay saltos de línea o URL-safe (`-`/`_`): usa `base64.urlsafe_b64decode` y quita espacios.
- **XOR con la clave equivocada da texto «casi legible»** → la longitud de clave es múltiplo; prueba longitudes divisoras.
- **El ZIP resultante está corrupto** → XOR solo afecta a la cabecera; revisa si la clave cambia a mitad o si hay un prefijo sin cifrar.
- **`file` dice `data`** → normal con XOR; no te fíes, aplica la fuerza bruta.

## 6. Detección y mitigación (lado real)

- XOR de un byte no es cifrado: cualquier DLP lo detecta por entropía y magic bytes tras transformación.
- En malware, las cadenas se ofuscan con XOR + base64; los YARA de familia suelen buscar la rutina de decodificación, no la clave.
- Para forense: guarda el blob original, el script y la clave usada; la cadena de custodia incluye la transformación.

MITRE: T1027 (ofuscación), T1140 (deobfuscación).
