---
challenge: Restaurant
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, ret2libc, buffer-overflow, rop, elf]
---

# Restaurant — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El binario de 64 bits tiene un desbordamiento de pila sin canario. Se filtra `puts@got` con una ROP de dos etapas, se calcula la base de libc y se llama a `system("/bin/sh")`. La libc se entrega junto al reto.

## Enunciado y superficie

- Pwn, Easy, retirado.
- Se entregan `restaurant` y `libc.so.6`.
- Servicio remoto por TCP.

```bash
file restaurant
checksec --file=restaurant
# NX, no PIE, no canary, full RELRO
```

## Reconocimiento

```bash
./restaurant
# menú / petición de entrada
```

El programa lee más bytes de los que reserva en la pila. El offset hasta el return address se calcula con `cyclic`/`pwndbg`:

```bash
gdb -q ./restaurant
cyclic 200
```

## Análisis

Al no haber PIE, las direcciones del binario son fijas. La primera etapa llama a `puts(puts@got)` y vuelve a `main` para repetir el desbordamiento. La segunda usa la fuga para calcular la base de libc y ejecutar `system("/bin/sh")`.

```python
rop = ROP(elf)
rop.call(elf.plt['puts'], [elf.got['puts']])
rop.call(elf.symbols['main'])
```

## Explicación del fallo

El programa no limita la longitud de la entrada y copia en un buffer de pila. Sin canario ni PIE, un ROP básico es suficiente; la libc entregada permite calcular `system` y `/bin/sh`.

## Reproducción local

1. Calcular el offset.
2. Construir la ROP de fuga.
3. Recibir la dirección de `puts`.
4. Calcular la base de libc.
5. Enviar la segunda ROP con `system("/bin/sh")`.

```python
libc.address = leak - libc.symbols['puts']
```

## Evidencia

- `checksec` y offset.
- Fuga de `puts` y base de libc calculada.
- Shell remota y flag redactada.

## Lecciones aprendidas

- Sin PIE, la ROP del binario es directa.
- Una fuga de GOT derrota ASLR de libc.
- Volver a `main` permite una segunda etapa.
- La libc del reto debe usarse para calcular offsets.

## Mitigación y detección

- Compilar con PIE, canario y `FORTIFY_SOURCE`.
- Validar longitudes de entrada.
- Usar `read` con tamaño acotado.
- En CTF, documentar la versión de libc.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/restaurant/>
- <https://docs.pwntools.com/>
- <https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/ret2libc/>
