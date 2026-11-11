---
challenge: Shattered Tablet
category: Reversing
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, ghidra, estatico, comparaciones]
---

# Shattered Tablet — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un ELF de 64 bits pide una cadena de 40 caracteres y la valida con **40 comparaciones independientes**, una por índice: `data[0] == 'H'`, `data[1] == 'T'`, etc. El orden de las condiciones está mezclado a propósito, pero cada una fija una posición. Reasignando el buffer como `char[64]` en Ghidra (o con un `pdf @ main` en radare2) se reconstruye la cadena ordenando por índice.

## Enunciado y superficie

- Categoría Reversing, dificultad Very Easy; reto de Cyber Apocalypse 2023.
- Se entrega un único binario, `tablet`, sin código fuente.
- El enunciado habla de una tableta de piedra que se rompe en pedazos: cada trozo es una condición.

## Reconocimiento

```bash
file tablet
./tablet
```

`file` lo identifica como ELF 64-bit LSB PIE, x86-64, enlazado dinámicamente y no stripped. Al ejecutarlo imprime `Hmmmm... I think the tablet says: ` y espera hasta 64 bytes por `stdin`; después responde `Yes! That's right!` o `No... not that`.

## Análisis del código

Ghidra muestra un `main` con ocho variables de 8 bytes (`local_48` a `local_10`) inicializadas a cero y un `fgets(data, 0x40, stdin)`. La comparación es una cadena de `&&` sobre bytes sueltos:

```c
if ((data[34] == '4') && (data[20] == '3') && (data[36] == 'r') &&
    (data[1] == 'T') && (data[21] == 'v') && (data[6] == '0') && ...
```

El decompilador enseña `local_28._2_1_`, `local_38._4_1_` y compañía porque trata el buffer como ocho `undefined8`. Al cambiar el tipo de `local_48` a `char[64]` y renombrarlo a `data`, las condiciones quedan legibles y ordenadas por índice.

## Explicación del fallo

No hay validación criptográfica ni ofuscación real: la cadena esperada está **codificada como 40 comparaciones**. Cada carácter se comprueba por separado, así que conocer la posición y el literal basta. El único trabajo es pasar de los desplazamientos de Ghidra (`local_28._2_1_`) a `data[34]`.

## Reproducción local

```bash
chmod +x tablet
./tablet
# introducir 40 caracteres y leer el veredicto
```

También se puede parchear la comparación para que imprima el buffer, pero no hace falta: el análisis estático ya da todos los caracteres.

## Explotación

1. Abrir `tablet` en Ghidra y localizar `main`.
2. Retype de `local_48` a `char[64]`; a partir de ahí las condiciones son `data[i] == 'x'`.
3. Copiar los pares `(i, 'x')` y ordenarlos por índice:

```python
pairs = [(34, '4'), (20, '3'), (36, 'r'), (1, 'T'), (21, 'v'), (6, '0'), (39, '}')]
buf = ['?'] * 40
for i, c in pairs:
    buf[i] = c
print(''.join(buf))
```

La lista completa son 40 pares; con todos, `''.join(buf)` es la flag. Alternativa sin decompilador: `radare2 -AA ./tablet`, `pdf @ main` y extraer los pares con una expresión regular sobre las comparaciones.

## Evidencia

- `tablet`, ELF 64-bit PIE no stripped.
- 40 condiciones `data[i] == literal` en `main`; la cadena reconstruida se guarda en `private/`.

## Lecciones aprendidas

- **Tipo del buffer**: sin reasignar `char[64]`, Ghidra muestra desplazamientos y el orden se pierde.
- **El orden de las condiciones no es el de la flag**: hay que ordenar por índice, no por aparición.
- **Longitud**: `fgets` admite 64 bytes, pero solo se comprueban 40; no hay que rellenar el resto.

## Mitigaciones y detección

- Comparar la cadena completa con `strcmp` no la protege mejor, pero evita filtrar la posición de cada carácter.
- Si el secreto debe residir en el cliente, derivarlo por usuario y verificar en servidor; cualquier literal embebido se extrae.
- Detección: binarios con decenas de comparaciones de bytes consecutivas contra constantes, típicas de checkers generados.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/shattered-tablet/>
- <https://bryanmcnulty.com/posts/htb-shattered-tablet>
- <https://ghidra-sre.org/>
