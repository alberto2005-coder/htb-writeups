---
title: Canario, PIE y ROP: de la fuga al shell
tags: [pwn, canary, pie, stack-pivot, ret2libc, aslr]
---

# Canario, PIE y ROP: de la fuga al shell

[🇬🇧 English](canary-pie-rop.en.md) | **Español**

## 1. Cuándo mirar aquí

El binario tiene canario, PIE y NX, y el desbordamiento llega justo al retorno. Antes de escribir una cadena hay que resolver tres cosas: el canario, la base del binario y la de libc. Si no queda espacio para la cadena, se añade un pivot.

## 2. El canario

Es un valor aleatorio de 8 bytes colocado entre el búfer y el `saved rbp`. En x86-64 el byte bajo es `00`, lo que permite filtrarlo con funciones de cadena y también reduce la fuerza bruta a 7 bytes.

- **Fuga directa**: `printf("%s")` o `write` sobre un búfer que lo incluya.
- **Fuerza bruta**: si el servidor hace `fork()` sin `exec`, todos los hijos comparten canario. Se prueba byte a byte (256 posibilidades) y se detecta el acierto porque el hijo responde en vez de morir.

```text
payload = relleno + candidato
si "Usuario encontrado" -> byte correcto
si el hijo muere        -> siguiente candidato
```

## 3. La base de PIE

El retorno de una función vuelve a una dirección del binario. Si se filtra (por la misma fuerza bruta o por un `%p`), la base es `retorno - offset_del_retorno`. Los 12 bits bajos de una dirección no cambian con ASLR, así que un offset conocido se puede usar como ancla.

```python
base = ret_leak - 0xecf
gadget = base + 0xf73
```

## 4. Pivotar la pila

Cuando el `read` termina exactamente en el retorno no hay sitio para más direcciones. `leave; ret` hace:

```asm
mov rsp, rbp
pop rbp
ret
```

Si el `saved rbp` apunta al búfer, la cadena continúa allí. Hay que calcular la distancia entre el `saved rbp` y el inicio del búfer, que depende del build y de las variables locales.

Alternativas: `pop rsp`, un `xchg rsp, rax` o una función que copie el payload a una zona escribible.

## 5. Cadena típica

1. `pop rdi; ret` → fd del socket.
2. `pop rsi; pop r15; ret` → dirección de `write@got`.
3. `pop rdx; ret` → 8.
4. `write@plt` → filtra la dirección real de `write`.
5. Volver a la función vulnerable para enviar la segunda cadena.
6. Con la base de libc: `dup2(fd, 0/1/2)` y `system("/bin/sh")` o `execve`.

Si el binario no tiene gadgets suficientes, `__libc_csu_init` ofrece el clásico ret2csu.

## 6. La entrada codificada

Si el programa aplica XOR a la entrada (por ejemplo `0xd`), **todo** el payload va codificado, incluidos canario y direcciones. Un byte sin codificar rompe el marco y el proceso muere sin explicación. El terminador `00` del canario se envía como `00 ^ clave`.

## 7. Errores típicos

- **Offset del retorno equivocado**: la base de PIE sale desplazada y todos los gadgets fallan.
- **Canario mal ordenado**: se prueba de izquierda a derecha, no al revés.
- **Distancia al búfer fija**: cambia entre builds; se mide en GDB con `$rbp - $rsp` o con un breakpoint tras el `read`.
- **fd del socket**: no siempre es 4; se prueban varios.
- **libc distinta**: los offsets de `system`, `dup2` y `/bin/sh` se confirman con el leak y libc.rip.
- **Pila desalineada**: `system` puede fallar por alineación; añadir un `ret` de más.

## 8. Detección y mitigación

- `fork()` + `exec()` por conexión para que el canario no se herede.
- `-fstack-protector-strong`, `-pie -fPIE`, `-Wl,-z,relro,-z,now` y `read` con `sizeof`.
- Detección: muchas conexiones que fallan en el mismo byte y una que responde distinto; payloads de tamaño exacto al marco; caídas repetidas.
- CWE-121, CWE-798; MITRE T1190.

Referencias: `man 3 read`, documentación de pwntools (`ROP`, `ELF`), libc.rip y las notas de stack pivoting de HackTricks.
