---
challenge: WIDE
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, wide-strings, ghidra]
---

# WIDE — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El binario ELF `wide` compara la entrada con cadenas almacenadas en UTF-16. `strings` normal no las muestra completas; `strings -el` y una búsqueda de cadenas anchas en Ghidra revelan la comparación y la clave.

## Enunciado y superficie

- Reversing, Very Easy, retirado.
- Se entrega un ELF de 64 bits y un archivo `db.ex`.
- El enunciado habla de una dimensión cifrada.

```bash
file wide db.ex
checksec ./wide
```

## Reconocimiento

```bash
strings -a wide | head
strings -a -el wide
```

- `wide` no está stripped.
- Las cadenas legibles aparecen separadas por bytes nulos.
- `db.ex` contiene la lista de dimensiones y códigos.

## Análisis del código

En Ghidra, la función principal recorre una tabla de nombres y compara la entrada con cada nombre usando una función de cadena ancha. La dimensión `Flaggle Alpha` es la única marcada como cifrada.

La comparación relevante usa `wchar_t`/UTF-16; por eso `strings` normal solo muestra fragmentos.

## Explicación del fallo

La "encriptación" es una comparación directa contra una cadena embebida. No hay derivación de clave ni criptografía: la clave está en `.rodata` como texto ancho.

## Reproducción local

```bash
chmod +x wide
./wide
# Introducir candidatos y observar la comparación
```

- En GDB, poner un breakpoint en la función de comparación.
- Inspeccionar `$rdi`/`$rsi` como cadenas UTF-16.
- Alternativamente, volcar `.rodata` y decodificar cada dos bytes.

## Explotación

```bash
strings -el wide | grep -i -E 'flag|dimension|alpha'
./wide
```

Se introduce la cadena encontrada y el binario imprime la flag. La flag se redacta.

## Evidencia

- Salida de `file` y `checksec`.
- `strings -el` con la cadena candidata.
- Captura de Ghidra de la comparación.
- Ejecución correcta sin mostrar la flag.

## Lecciones aprendidas

- `strings` por defecto no detecta UTF-16.
- Un binario "ofuscado" puede seguir siendo una comparación simple.
- Revisar el ancho de los caracteres antes de concluir que no hay texto.

## Mitigaciones y detección

- No almacenar secretos en binarios distribuidos.
- Usar derivación de clave y comparación en tiempo constante si se valida una licencia.
- Ofuscar no sustituye a un diseño seguro.

## Referencias

- <https://www.hackthebox.com/challenges/WIDE>
- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/wide/>
- <https://attack.mitre.org/techniques/T1027/>
