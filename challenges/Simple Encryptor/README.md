---
challenge: Simple Encryptor
category: Reversing
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, prng, xor, rotacion, ctypes]
---

# Simple Encryptor — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Se entrega `encrypt` y `flag.enc`. El binario lee `flag`, siembra `srand(time(NULL))`, cifra cada byte con `b ^= rand()` y luego `ROL(b, rand() & 7)`, y escribe **la semilla en los cuatro primeros bytes** del fichero. Con esa semilla se reproduce la secuencia y se invierte el cifrado: `ROR` y XOR en orden inverso. Hay que hacerlo con glibc.

## Enunciado y superficie

- Categoría Reversing, dificultad Very Easy.
- Entrega: `encrypt` (ELF de 64 bits) y `flag.enc`.
- El enunciado plantea un ransomware: la flag original ya no está, pero quedan el cifrador y el fichero cifrado.

## Reconocimiento

```bash
file encrypt flag.enc
strings -n 6 encrypt | head
xxd flag.enc | head
```

`strings` muestra `srand`, `fopen`, `ftell` y `time`: la pista del PRNG. `flag.enc` empieza por cuatro bytes que no son texto; el resto es el cuerpo cifrado.

## Análisis del código

El `main` descompilado en Ghidra/IDA hace, en este orden:

```c
stream = fopen("flag", "rb");
fseek(stream, 0, SEEK_END);
size = ftell(stream);
fseek(stream, 0, SEEK_SET);
buf = malloc(size);
fread(buf, size, 1, stream);
fclose(stream);

seed = time(NULL);
srand(seed);
for (i = 0; i < size; i++) {
    buf[i] ^= rand();
    r = rand();
    buf[i] = ROL8(buf[i], r & 7);
}

out = fopen("flag.enc", "wb");
fwrite(&seed, 1, 4, out);
fwrite(buf, 1, size, out);
```

- La semilla va en claro al principio del fichero: no hay que adivinarla.
- Cada byte consume **dos** salidas de `rand()`: una para el XOR y otra para el desplazamiento.
- `ROL8` es una rotación, no un shift: los bits que salen por la izquierda entran por la derecha.

## Explicación del fallo

El cifrado es reversible con la semilla, y la semilla está en el propio fichero. El XOR con `rand() & 0xff` y la rotación de 0 a 7 bits no aportan secreto: la única incógnita era el estado del PRNG, que se entrega.

## Reproducción local

Se puede recompilar el cifrador a partir del seudocódigo y cifrar un `flag` de prueba para comprobar que el descifrador devuelve el mismo contenido. El binario original espera un fichero llamado `flag` en el directorio actual.

## Explotación

Descifrador con `ctypes` sobre la libc del sistema, que es la misma que usa el binario:

```python
import ctypes

libc = ctypes.CDLL("libc.so.6")
raw = bytearray(open("flag.enc", "rb").read())

seed = int.from_bytes(raw[:4], "little")
libc.srand(seed)

out = bytearray()
for b in raw[4:]:
    r1 = libc.rand()
    r2 = libc.rand()
    k = r2 & 7
    b = ((b >> k) | (b << (8 - k))) & 0xff   # ROR
    out.append(b ^ (r1 & 0xff))

print(out.decode())
```

Notas:

- El orden importa: al descifrar se deshace primero la rotación y después el XOR.
- Con `k = 0`, `b << 8` se enmascara a `0xff` y la rotación deja el byte igual.
- Python no sirve con `random`: su Mersenne Twister no es el `rand()` de C. Tampoco vale la CRT de Windows.

## Evidencia

- `encrypt`, ELF 64-bit dinámico.
- `flag.enc` con 4 bytes de semilla y el cuerpo cifrado.
- Texto descifrado con el prefijo habitual de HTB; se guarda en `private/`.

## Lecciones aprendidas

- **Leer la semilla del fichero**: el primer intento fue probar timestamps cercanos a la fecha del reto; era innecesario.
- **Orden de las operaciones**: aplicar XOR antes que `ROR` da basura legible a medias.
- **PRNG equivocado**: `python -c "import random"` no reproduce `rand()` de glibc; hay que llamar a la libc.

## Mitigaciones y detección

- No se cifra con un PRNG sembrado por el reloj ni se guarda la semilla junto al ciphertext: eso convierte el cifrado en una codificación reversible.
- Para cifrado real: AES-GCM o ChaCha20-Poly1305 con nonce aleatorio y clave fuera del artefacto.
- Detección: ficheros cuyo primer campo de 4 bytes es un timestamp UNIX plausible seguido de datos de alta entropía; YARA por la tríada `time`/`srand`/`fwrite`.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/simple-encryptor/>
- <https://blog.loganthompson.de/posts/htb-simple-encryptor>
- <https://man7.org/linux/man-pages/man3/rand.3.html>
