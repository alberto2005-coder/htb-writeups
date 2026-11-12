---
challenge: Baby Crypt
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, xor, ghidra, gdb]
---

# Baby Crypt — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin flags reales.

## TL;DR

Un ELF pide una clave de tres bytes y descifra un bloque de 26 bytes con XOR. El bloque cifrado está en el binario y el texto claro esperado empieza por el prefijo de flag de HTB (`HTB` + `{`), así que los tres primeros bytes de la clave se obtienen con `clave[i] = cifrado[i] ^ claro[i]`. Con la clave `w0w` el programa imprime la flag.

## Enunciado y superficie

- Reversing, Easy, retirado.
- Se entrega un binario `baby_crypt`.
- No hay servidor: todo ocurre en local.

```bash
file baby_crypt
checksec --file=baby_crypt
```

```text
ELF 64-bit LSB shared object, x86-64, not stripped
```

## Reconocimiento

El binario no está stripped, así que `main` aparece en Ghidra. También se puede empezar por `strings`:

```bash
strings -a baby_crypt | head -30
```

La cadena que pide la clave y el mensaje de error son visibles, pero la flag no: se calcula en runtime.

## Análisis del código

La función principal reserva 4 bytes para la clave, lee hasta 3 caracteres y ejecuta un XOR sobre un bloque local:

```c
key = malloc(4);
fgets(key, 4, stdin);

local_38 = 0x6f0547480c35643f;
local_30 = 0x28130304026f0446;
local_28 = 0x05000f4358280e52;
local_20 = 0x4d56;

for (i = 0; i < 0x1a; i++)
    *((byte *)&local_38 + i) ^= key[i % 3];

printf("%.26s\n", &local_38);
```

El bloque se almacena en little-endian. Los primeros bytes del ciphertext son `3f 64 35 ...`; el plaintext esperado empieza por `H T B`.

## Explicación del fallo

XOR es simétrico: `c = p ^ k` implica `k = c ^ p`. Como se conoce el formato de la flag, no hace falta fuerza bruta. El programa compara implícitamente el resultado con el formato esperado al imprimirlo; la clave correcta produce texto legible.

```text
k[0] = 0x3f ^ ord('H') = 'w'
k[1] = 0x64 ^ ord('T') = '0'
k[2] = 0x35 ^ ord('B') = 'w'
```

## Reproducción local

```bash
chmod +x baby_crypt
./baby_crypt
# Give me the key and I'll give you the flag:
w0w
```

Para verificar la hipótesis sin ejecutar:

```python
ct = bytes.fromhex('3f6435...')   # 26 bytes
key = bytes([ct[0]^ord('H'), ct[1]^ord('T'), ct[2]^ord('B')])
pt = bytes(b ^ key[i % 3] for i, b in enumerate(ct))
print(pt.decode())
```

En Ghidra se puede renombrar el buffer y cambiar el tipo a `char[26]` para leer el bloque completo.

## Explotación

No hay exploit remoto: la "explotación" es recuperar la clave y ejecutar el binario.

```bash
printf 'w0w\n' | ./baby_crypt
```

La salida correcta contiene la flag; se redacta en la evidencia.

## Evidencia

- Descompilado de `main` con el bucle XOR.
- Cálculo de los tres bytes de clave.
- Ejecución con `w0w` y flag redactada.

## Lecciones aprendidas

- Un XOR con clave repetida y texto claro conocido se rompe sin fuerza bruta.
- El formato de la flag es un known-plaintext de tres bytes.
- Little-endian importa al leer constantes de 64 bits.
- Ghidra y `gdb` son suficientes; no hace falta un framework de reversing.

## Mitigaciones y detección

- No usar XOR con clave corta para proteger secretos.
- Si se ofusca una comprobación, no se debe almacenar el texto claro esperado en el mismo binario.
- Para CTF, documentar la constante y el offset exactos del build.
- En software real, usar AES-GCM o ChaCha20-Poly1305 con claves gestionadas fuera del binario.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/baby-crypt/>
- <https://ghidra-sre.org/>
- <https://sourceware.org/gdb/current/onlinedocs/gdb/>
