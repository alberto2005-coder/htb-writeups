---
challenge: Bat Computer
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, binary, patch, serial, ghidra]
---

# Bat Computer — Hack The Box (Challenge)

[🐬 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un binario pide una contraseña y compara caracteres con una transformación sencilla. El análisis estático con `strings` y un desensamblador revela la lógica; se reconstruye la entrada válida o se parchea la comparación para obtener la flag.

## Enunciado y superficie

- Reversing, Easy, retirado.
- Se entrega un ejecutable y una descripción del reto.
- El objetivo es encontrar la entrada correcta.

```bash
file bat-computer
strings -n 6 bat-computer | head
```

## Reconocimiento

```bash
chmod +x bat-computer
./bat-computer
ltrace ./bat-computer
```

- El binario es un ejecutable nativo.
- Pide una cadena y muestra un mensaje de éxito o error.
- `strings` revela mensajes y posibles constantes.

## Análisis

Se abre en Ghidra/objdump y se localiza `main`. La comparación recorre la entrada, aplica una XOR o una suma y la compara con una tabla. Se documentan las constantes y se invierte la transformación.

```c
for (i = 0; i < len; i++)
    if ((input[i] ^ key[i]) != target[i]) return 1;
```

## Explotación

Se reconstruye la entrada con un script o se cambia el salto condicional para aceptar cualquier cadena. La flag se muestra al ejecutar el binario con la entrada válida; no se publica.

```python
print(bytes(a ^ b for a, b in zip(target, key)))
```

## Evidencia

- Lógica de comparación identificada.
- Entrada reconstruida o parche aplicado.
- Mensaje de éxito y flag.

## Lecciones aprendidas

- `strings` y `ltrace` aceleran el triaje.
- Una transformación simple se invierte con un script.
- Parchear un salto es útil para validar la ruta.
- Documentar constantes y offsets facilita repetir el análisis.

## Mitigaciones y detección

- No proteger secretos con comprobaciones locales.
- Ofuscar no sustituye la criptografía.
- Firmar binarios y verificar su integridad.
- Revisar ejecutables que contienen cadenas de flag o claves.
- Referencias: Ghidra, x86 reversing.

## Referencias

- <https://www.hackthebox.com/challenges/Bat%20Computer>
- <https://ghidra-sre.org/>
- <https://en.wikipedia.org/wiki/Disassembler>
- <https://attack.mitre.org/techniques/T1027/>
