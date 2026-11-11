---
challenge: FlagCasino
category: Reversing
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, prng, rand, ctypes]
---

# FlagCasino — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un ELF de 64 bits pide la flag **carácter a carácter**. Para cada carácter hace `srand(c)` y compara `rand()` con una entrada del array `check`. Como la semilla es el propio carácter, basta recorrer los 95 imprimibles, generar el primer `rand()` de cada semilla y quedarse con el carácter cuyo valor coincide con `check[i]`. Treinta comparaciones, treinta caracteres.

## Enunciado y superficie

- Categoría Reversing, dificultad Very Easy; reto de Business CTF 2024.
- Se entrega un único binario, `casino`, sin código fuente.
- El enunciado habla de un casino abandonado y robots que aceptan apuestas: la «apuesta» es la flag.

## Reconocimiento

```bash
file casino
./casino
```

`file` lo identifica como ELF 64-bit LSB, x86-64, enlazado dinámicamente y **no stripped**. Al ejecutarlo imprime un banner ASCII y pide entrada con `> `. Cualquier carácter que no sea el esperado responde `[ * INCORRECT * ]` y termina con el aviso de evacuación.

`strings` no da la flag: el binario no la guarda, la **valida**.

## Análisis del código

En Ghidra, `main` queda así de corto:

```c
i = 0;
while (true) {
    if (29 < i) { puts("[ ** HOUSE BALANCE $0 - PLEASE COME BACK LATER ** ]"); return 0; }
    printf("> ");
    if (__isoc99_scanf(" %c", &c) != 1) break;
    srand((int)c);
    if (rand() != check[i]) {
        puts("[ * INCORRECT * ]");
        exit(-2);
    }
    puts("[ * CORRECT *]");
    i++;
}
```

- `check` es un `int[30]` en `.data`, en `0x104080`, con 30 valores de 32 bits.
- El bucle recorre `i = 0..29`: la flag tiene **30 caracteres**.
- `srand(c)` usa el carácter introducido como semilla y `rand()` es la primera salida de esa semilla.

## Explicación del fallo

La comprobación no usa un hash ni una clave: usa un PRNG **sembrado con el dato secreto**. `rand()` es determinista para una semilla dada, así que el valor esperado en `check[i]` identifica la semilla que lo produce. El espacio de semillas es el de los caracteres imprimibles (95 posibilidades), no el de la flag completa.

## Reproducción local

```bash
chmod +x casino
./casino
# introducir caracteres a mano para ver el veredicto por posición
```

También se puede depurar con GDB y poner un breakpoint en la comparación para leer `check[i]` y el `rand()` calculado en cada iteración.

## Explotación

Con `pwntools` se lee el array directamente del ELF y con `ctypes` se reproduce el `rand()` de la libc del sistema:

```python
import ctypes
from pwn import ELF

libc = ctypes.CDLL("libc.so.6")
mapping = {}
for c in range(0x20, 0x7f):
    libc.srand(c)
    mapping[libc.rand()] = chr(c)

e = ELF("./casino", checksec=False)
flag = "".join(mapping[e.u32(e.sym["check"] + i * 4)] for i in range(30))
print(flag)
```

Alternativa en C, sin pwntools: copiar el array desde Ghidra a un `int check[30]` y hacer el mismo doble bucle `srand(c); rand()` para `c` entre `0x20` y `0x7e`.

Detalle importante: la libc de Linux y la de Windows **no generan la misma secuencia** con la misma semilla. El binario es ELF, así que la reproducción tiene que hacerse con glibc.

## Evidencia

- `casino`, ELF 64-bit no stripped.
- Array `check` de 30 enteros en `0x104080`.
- Salida `[ * CORRECT *]` repetida 30 veces con la secuencia correcta; la flag se guarda en `private/`.

## Lecciones aprendidas

- **Semilla = dato**: si el PRNG se siembra con el secreto, cada comparación se resuelve por fuerza bruta de 95 semillas, no de la flag.
- **Copiar el array mal**: leer `check` como bytes en lugar de `uint32` desplaza los valores y no coincide ninguna posición.
- **Probar en otro SO**: la secuencia de `rand()` cambia entre glibc y la CRT de Windows.

## Mitigaciones y detección

- No se valida un secreto con un PRNG sembrado por el propio secreto: es una tabla de búsqueda de 95 entradas.
- Para comparaciones reales, usar un KDF con sal (Argon2, scrypt) y comparación en tiempo constante.
- Detección: binarios que llaman a `srand` con entrada del usuario y comparan `rand()` contra una tabla constante; YARA puede buscar el patrón `srand`/`rand`/array de 32 bits.

## Referencias

- <https://github.com/hackthebox/business-ctf-2024/tree/main/reversing/%5BVery%20Easy%5D%20FlagCasino>
- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/flagcasino/>
- <https://man7.org/linux/man-pages/man3/rand.3.html>
