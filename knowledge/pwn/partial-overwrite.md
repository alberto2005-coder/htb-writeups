---
title: Sobrescritura parcial de direcciones
tags: [pwn, buffer-overflow, partial-overwrite, aslr, pie, x86-64]
---

# Sobrescritura parcial de direcciones

[🇬🇧 English](partial-overwrite.en.md) | **Español**

## 1. Cuándo mirar aquí

Un desbordamiento deja escribir menos bytes de los que ocupa una dirección, o el programa solo lee un byte de más. Si el binario no tiene PIE, la dirección de retorno ya es conocida y basta cambiar su byte bajo para saltar a otra rama del mismo binario.

## 2. Por qué funciona

Las direcciones de un ELF sin PIE son fijas (`0x400000` + offset). El byte bajo de la dirección de retorno apunta a la instrucción siguiente a la llamada; cambiándolo se puede entrar en otra instrucción del mismo bloque o de una rama cercana.

```text
retorno original: 0x0000000000400ba0
byte bajo:                         ^^
nuevo destino:    0x0000000000400b01
```

No hace falta escribir los seis bytes altos ni filtrar ASLR: no cambian.

## 3. Cuántos bytes se pueden cambiar

- **1 byte**: alcanza cualquier destino dentro del mismo bloque de 256 bytes que el retorno original, sin cambiar de página.
- **2 bytes**: cubre 64 KB; útil para saltar a otra función del binario si la página no cambia.
- **3 bytes o más**: ya se pisa parte de la dirección y hay que conocerla.

El límite lo pone el `read`: si el búfer está a 40 bytes del retorno y se leen 57, solo entra un byte.

## 4. Calcular el offset

```bash
python3 -c "from pwn import *; print(cyclic(100))"
```

Se envía el patrón, se mira `$rsp` en el crash y se busca el desplazamiento:

```gdb
pattern search $rsp
```

Entre el búfer y el retorno puede haber variables locales y el `saved RBP`; no se asume que el offset sea el tamaño del búfer.

## 5. Elegir el destino

Desensamblar la función y localizar la rama que interesa:

```bash
objdump -d -M intel binario | sed -n '/<funcion>:/,/^$/p'
```

Se busca una instrucción cuya dirección comparta los bytes altos con el retorno y solo difiera en el byte bajo. En un CTF suele haber una rama que imprime la flag o llama a `system` a pocos bytes.

## 6. Límites

- **PIE**: las direcciones cambian por ejecución; hace falta filtrar la base (o usar un parcial de 12 bits, que no cambia con ASLR).
- **Canario**: si está entre el búfer y el retorno, hay que filtrarlo antes.
- **ASLR y página**: cambiar el byte bajo no cruza de página; si el destino está en otra, hacen falta más bytes.
- **Recompilación**: cualquier cambio mueve las direcciones y el byte calculado deja de servir.

## 7. Detección y mitigación

- `-fstack-protector-strong` y `-pie -fPIE` convierten el fallo en algo que requiere fuga y canario.
- Sustituir `read` por `fgets`/`read` con `sizeof`.
- Detección: crashes con `RIP` en el binario tras entradas de longitud exacta; patrones de relleno seguidos de un byte de control.
- CWE-121; MITRE T1190.

Referencias: documentación de pwntools (`cyclic`, `ELF`), CWE-121 y las notas de ASLR de Linux.
