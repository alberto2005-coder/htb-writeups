---
challenge: Baby RE
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, ltrace, strcmp, dynamic-analysis]
---

# Baby RE — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El binario pide una clave y la compara con `strcmp`. `ltrace` muestra la llamada y el valor esperado sin necesidad de descompilar. Al introducir esa clave, el programa imprime la flag.

## Enunciado y superficie

- Reversing, Very Easy, retirado.
- Se entrega un ejecutable ELF llamado `baby`.
- El programa pide una clave por entrada estándar.

```bash
file baby
./baby
```

## Reconocimiento

- ELF 64 bits, no stripped, enlazado dinámicamente.
- `strings` muestra el prompt y el mensaje de error.
- `checksec` indica las protecciones; para este reto no son el obstáculo.

```bash
strings -n 5 baby | head
checksec --file=baby
```

## Análisis del código

La función principal lee la entrada con `fgets` y la compara con una cadena constante mediante `strcmp`. La cadena está en `.rodata` y también aparece en la traza dinámica.

```bash
ltrace ./baby
```

La salida muestra:

```text
strcmp("<INPUT>", "<KEY>")
```

## Explicación del fallo

La validación es una comparación local. No hay ofuscación ni comprobación remota: el valor esperado está en el binario y se puede extraer con `strings`, `ltrace`, un debugger o Ghidra. La clave no es un secreto criptográfico.

## Reproducción local

```bash
chmod +x baby
printf '<KEY>\n' | ./baby
```

- `ltrace` requiere que el binario sea ejecutable.
- Si la entrada incluye salto de línea, `fgets` lo conserva y `strcmp` compara con la cadena esperada.

## Explotación

1. Ejecutar `ltrace ./baby`.
2. Introducir cualquier valor.
3. Leer la segunda cadena de `strcmp`.
4. Repetir con esa clave.

```bash
printf '<KEY>\n' | ./baby
```

El programa imprime la flag; se redacta.

## Evidencia

- Salida de `ltrace` con la clave redactada.
- Ejecución correcta y flag redactada.
- `file` y `strings` del binario.

## Lecciones aprendidas

- Una comparación local no protege un secreto.
- `ltrace` es suficiente cuando el binario usa funciones de biblioteca.
- `strings` y Ghidra permiten el mismo resultado sin ejecutar.

## Mitigaciones y detección

- No almacenar claves ni flags en el cliente.
- Validar en el servidor y usar un protocolo con autenticación.
- Ofuscar no sustituye a un diseño seguro, pero eleva el coste.
- Para retos, rotar el valor esperado y no reutilizarlo en producción.

## Referencias

- <https://www.hackthebox.com/challenges/Baby%20RE>
- <https://man7.org/linux/man-pages/man1/ltrace.1.html>
- <https://attack.mitre.org/techniques/T1027/>
