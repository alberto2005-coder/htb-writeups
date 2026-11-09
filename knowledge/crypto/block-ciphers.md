---
title: Cifrados de bloque y cifrados propios (ECB, TEA, afín)
tags: [crypto, aes, ecb, tea, ctf]
---

# Cifrados de bloque y cifrados propios

[🇬🇧 English](block-ciphers.en.md) | **Español**

## 1. Reconocer el cifrado

- **AES-ECB**: bloques de 16 bytes; el mismo bloque de texto produce el mismo bloque de cifrado. Se detecta por repeticiones.
- **TEA/XTEA**: bloques de 8 bytes, constante `delta = 0x9E3779B9`, 32 rondas por defecto.
- **Cifrado propio**: una función lineal o una permutación sobre bytes; se invierte leyendo el código.

Empieza por tamaño y patrones:

```bash
wc -c cipher.bin
python3 -c "d=open('cipher.bin','rb').read(); print(len(d), len(d)%16, len(d)%8)"
```

## 2. AES-ECB

Detección por bloques repetidos:

```python
from collections import Counter
d = open('cipher.bin','rb').read()
blocks = [d[i:i+16] for i in range(0, len(d), 16)]
print(Counter(blocks).most_common(3))
```

Con texto conocido (el reto suele dar un `sample` claro), alinea bloques y compara: cada bloque de 16 bytes se ataca por separado. Para un oráculo *byte-at-a-time*, se rellena con `A` hasta que el byte objetivo cae al final de un bloque y se compara con un diccionario de 256 candidatos.

```bash
openssl enc -d -aes-128-ecb -K <hex_key> -in cipher.bin
```

## 3. TEA

Implementación de referencia (descifrado):

```python
def tea_decrypt(v, k):
    v0, v1 = v
    delta = 0x9E3779B9
    s = (delta * 32) & 0xFFFFFFFF
    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + k[2]) ^ (v0 + s) ^ ((v0 >> 5) + k[3]))) & 0xFFFFFFFF
        v0 = (v0 - (((v1 << 4) + k[0]) ^ (v1 + s) ^ ((v1 >> 5) + k[1]))) & 0xFFFFFFFF
        s = (s - delta) & 0xFFFFFFFF
    return v0, v1
```

Cuidado con el **orden de las mitades** y con el `& 0xFFFFFFFF` en cada operación: sin la máscara, Python crece sin límite y el resultado no coincide. Si el reto usa una variante (XTEA, número de rondas distinto), el `delta` y el bucle lo delatan.

## 4. Cifrados propios y clásicos

- **Afín módulo 256**: `c = (a*m + b) % 256`; se invierte con `pow(a, -1, 256)` si `gcd(a,256)=1`.
- **Permutación de bloques**: invierte la permutación leyendo el código; si es de 3 bytes, reconstruye en orden.
- **César/Trithemius**: el desplazamiento puede ser el índice del carácter (`+i`), no una constante. Prueba ambos.

```python
pt = bytes((c - b) * pow(a, -1, 256) % 256 for c in ct)
```

## 5. Errores típicos

- **ECB «no se ve»** → el texto es corto o el padding rompe la alineación; prueba a desplazar un byte.
- **TEA da basura** → endianness de la clave o de las mitades, o rondas distintas de 32.
- **`pow(a, -1, 256)` falla** → `a` es par; el cifrado no es invertible con ese módulo, revisa el código.
- **El descifrado «casi» sale** → un byte de diferencia suele ser una suma módulo 256 mal aplicada.

## 6. Detección y mitigación (lado real)

- ECB filtra patrones: usa CBC/GCM con IV aleatorio y autenticación.
- Cifrados propios sin análisis son la causa más común de fallos en CTF y en productos reales.
- TEA está obsoleto; XTEA/XXTEA tampoco se recomiendan para nuevos diseños.
- Documenta el modo y el padding: la mitad de los «fallos criptográficos» son de implementación.

MITRE: T1600.
