---
challenge: Oddly Even
category: Challenge
type: Coding
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [coding, python, parity, modulo, stdin-stdout]
---

# Oddly Even — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

El reto más corto de la categoría: leer un número y escribir `odd` o `even`. No hay binario, ni servicio, ni trampa criptográfica; solo comprobar que el programa lee bien la entrada y distingue par de impar, incluido el cero y los negativos.

## Enunciado y superficie

- Categoría **Coding**, dificultad **Very Easy**.
- La plataforma ofrece un editor (C, C++, Python o Rust) y un enunciado.
- Entrada: un entero.
- Salida: `odd` si es impar, `even` si es par.

```text
Entrada
3

Salida
odd
```

## Reconocimiento

No hay nada que escanear. Conviene fijar el contrato exacto:

- La salida es en minúsculas y sin texto adicional.
- `0` es par.
- Los negativos también cuentan: en Python `-3 % 2` es `1`, así que la comprobación funciona sin `abs()`.

## Análisis del código

No hay código previo. La solución cabe en una condición:

```python
n = int(input())
print("even" if n % 2 == 0 else "odd")
```

En C, el operador `%` con negativos puede devolver `-1`, así que la comparación correcta es `n % 2 != 0` para impar, no `n % 2 == 1`.

## Explicación del fallo

No hay vulnerabilidad. El único riesgo es enviar texto de más (`Odd`, `impar`, un salto extra) o usar una comparación que falle con negativos en C/C++.

## Reproducción local

```bash
for n in 3 0 -3; do printf '%s\n' "$n" | python3 oddly_even.py; done
```

```python
# oddly_even.py
n = int(input())
print("even" if n % 2 == 0 else "odd")
```

## Explotación

1. Leer el entero.
2. Imprimir `even` o `odd` en minúsculas.
3. Enviar la solución; la plataforma valida y devuelve la flag.

## Evidencia

- Salida local para `3`, `0` y `-3`.
- Sin flag real en la ficha.

## Lecciones aprendidas

- Los retos de coding miden el contrato de entrada/salida tanto como el algoritmo.
- El comportamiento del módulo con negativos cambia entre lenguajes; conviene probarlo.
- Escribir la cadena exacta (`odd`/`even`) evita fallos tontos de validación.

## Mitigaciones y detección

- No aplica: no hay componente de seguridad.
- Como hábito, validar el rango de entrada y el formato de salida en cualquier parser.

## Referencias

- <https://www.hackthebox.com/challenges/oddly-even>
- <https://x3ric.com/blog/posts/HackTheBox-Oddly-Even-Challenge>
- <https://7rocky.github.io/en/ctf/htb-challenges/coding/oddly-even/>
- <https://motasem-notes.net/practical-coding-in-cyber-security-hackthebox-coding-challenges>
