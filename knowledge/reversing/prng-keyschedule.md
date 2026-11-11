---
title: PRNG, semillas y esquemas de clave
tags: [reversing, prng, rand, glibc, ctypes, ctf]
---

# PRNG, semillas y esquemas de clave

[🇬🇧 English](prng-keyschedule.en.md) | **Español**

## 1. Cuándo mirar aquí

Un binario llama a `srand`/`rand` y el resultado decide si la entrada es correcta, o guarda la semilla junto al ciphertext. Dos patrones:

- `srand(entrada); if (rand() != tabla[i])`: el secreto es la semilla y se prueba por fuerza bruta.
- `srand(time(NULL))` y la semilla escrita en el fichero: el cifrado es reversible.

Antes de escribir nada, comprobar qué PRNG usa:

```bash
strings -n 5 binario | grep -E "srand|rand|time|random"
objdump -d -M intel binario | grep -E "call.*(srand|rand)"
```

## 2. `rand()` de glibc

`rand()` no es un generador criptográfico: en glibc es un generador aditivo de retroalimentación (algoritmo `TYPE_3`), con estado por proceso. `srand(seed)` fija ese estado y la secuencia es **determinista** para la misma semilla y la misma libc.

```c
srand(seed);
int r1 = rand();   // 0 .. RAND_MAX (2^31 - 1 en glibc)
```

Consecuencias prácticas:

- La secuencia de glibc **no coincide** con la de la CRT de Windows ni con `random` de Python (Mersenne Twister).
- Si el binario es ELF, reproducir con la libc de Linux; si es PE, con la CRT de Windows o con una implementación equivalente.
- `rand()` devuelve 31 bits útiles; para un byte se usa `rand() & 0xff`.

## 3. Reproducir la secuencia desde Python

`ctypes` llama a la libc del sistema, que es la misma que usa el binario:

```python
import ctypes

libc = ctypes.CDLL("libc.so.6")
libc.srand(1234)
print([libc.rand() for _ in range(5)])
```

Para invertir un mapeo de semillas (FlagCasino), se genera el primer `rand()` de cada semilla imprimible y se guarda en un diccionario:

```python
mapping = {}
for c in range(0x20, 0x7f):
    libc.srand(c)
    mapping[libc.rand()] = chr(c)
```

## 4. Semilla dentro del fichero

Si el formato es `[4 bytes de semilla][ciphertext]`, la semilla se lee como entero little-endian y se reproduce la secuencia:

```python
raw = open("flag.enc", "rb").read()
seed = int.from_bytes(raw[:4], "little")
libc.srand(seed)
for b in raw[4:]:
    ...
```

Cada byte puede consumir **una o dos** salidas de `rand()` según el esquema (XOR y rotación, por ejemplo). Hay que seguir el orden exacto del binario y deshacerlo al revés.

## 5. Rotaciones

`ROL8(b, k)` no es `b << k`: los bits que salen por la izquierda vuelven por la derecha.

```python
def rol(b, k):
    k &= 7
    return ((b << k) | (b >> (8 - k))) & 0xff

def ror(b, k):
    k &= 7
    return ((b >> k) | (b << (8 - k))) & 0xff
```

Con `k = 0`, la expresión `b << 8` se enmascara y el byte no cambia; conviene tratarlo explícitamente para no depender del enmascarado.

## 6. Mersenne Twister y `randcrack`

Cuando el objetivo es Python (`random`) o un servicio que expone salidas de MT19937, no basta con adivinar la semilla: con **624 salidas de 32 bits** se reconstruye el estado interno y se predicen las siguientes.

```bash
pip install randcrack
```

```python
from randcrack import RandCrack
rc = RandCrack()
for value in outputs[:624]:
    rc.submit(value)
print(rc.predict_getrandbits(32))
```

## 7. Errores típicos

- **Reproducir en otro SO**: la secuencia cambia; comprobar `file` y usar la libc correcta.
- **Consumir una sola salida por byte**: si el binario llama dos veces a `rand()`, todo el resto se desalinea.
- **Confundir shift con rotación**: los bits se pierden y el texto sale «casi» legible.
- **Semilla mal leída**: `int.from_bytes(..., "little")` frente a big-endian; probar ambas si el resultado es basura.
- **`RAND_MAX` distinto**: asumir 32 bits cuando la libc devuelve 31 cambia las máscaras.

## 8. Detección y mitigación (lado real)

- Un PRNG no es un CSPRNG: para tokens, claves y nonces se usa `secrets`, `os.urandom` o el CSPRNG del sistema.
- No se guarda la semilla junto al ciphertext ni se siembra con el reloj: convierte el cifrado en una codificación reversible.
- Detección: ficheros con un timestamp UNIX plausible en los primeros 4 bytes seguidos de datos de alta entropía; binarios con `srand`/`rand` en la ruta de validación.

MITRE: T1027 (ofuscación), T1140 (deobfuscación). Referencias: `man 3 rand`, el código de `random_r.c` de glibc y la documentación de `randcrack`.
