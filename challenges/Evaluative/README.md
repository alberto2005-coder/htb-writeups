---
challenge: Evaluative
category: Challenge
type: Coding
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [coding, python, polynomial, horner, stdin-stdout]
---

# Evaluative — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Reto de programación sin binario ni servicio: hay que evaluar un polinomio de grado 8 con nueve coeficientes y un valor de `x`, y devolver el resultado por stdout. La única trampa es no equivocarse con los exponentes; con el esquema de Horner sale en una línea y sin potencias grandes.

## Enunciado y superficie

- Categoría **Coding**, dificultad **Very Easy**.
- No entrega ficheros: la plataforma muestra el enunciado y un editor para enviar la solución (C, C++, Python o Rust).
- Entrada: los nueve coeficientes `a0 … a8` en una línea y, en otra, el entero `x`.
- Salida: `P(x) = a0 + a1·x + a2·x² + … + a8·x⁸`.

```text
Entrada
1 -2 3 -4 5 -6 7 -8 9
5

Salida
2983941
```

## Reconocimiento

No hay superficie que enumerar: es un problema de entrada/salida. Lo que conviene fijar antes de escribir:

- El orden de los coeficientes es de menor a mayor grado (`a0` primero).
- `x` puede ser negativo; las potencias pares serán positivas y las impares negativas.
- El resultado cabe en un entero de 64 bits para los rangos del reto, pero en Python no hay que preocuparse.

## Análisis del código

No hay código que analizar. El "análisis" es del enunciado: se pide una evaluación polinómica, no una raíz ni una derivada. Cualquier intento de resolver ecuaciones está fuera de lugar.

La forma directa es sumar `coeficiente * x**indice`. La forma eficiente es Horner, que evita calcular potencias y hace nueve multiplicaciones:

```text
P(x) = a0 + x·(a1 + x·(a2 + … + x·a8))
```

## Explicación del fallo

Aquí no hay vulnerabilidad: el ejercicio mide precisión al implementar una fórmula. Los errores típicos son de índice (empezar por `a1`), de signo con `x` negativo y de leer la entrada como una sola línea cuando viene en dos.

## Reproducción local

```bash
python3 evaluative.py <<'EOF'
1 -2 3 -4 5 -6 7 -8 9
5
EOF
```

```python
# evaluative.py
coeffs = list(map(int, input().split()))
x = int(input())

result = 0
for c in reversed(coeffs):
    result = result * x + c
print(result)
```

La variante con `enumerate` da el mismo resultado y es más legible:

```python
print(sum(c * x**i for i, c in enumerate(coeffs)))
```

## Explotación

1. Leer los coeficientes con `input().split()`.
2. Leer `x` con `int(input())`.
3. Evaluar con Horner y `print`.
4. Pegar la salida en la plataforma; el entorno devuelve la flag al acertar.

## Evidencia

- Ejecución local con el ejemplo y el resultado `2983941`.
- Sin flag real en la ficha.

## Lecciones aprendidas

- Horner no es solo optimización: evita desbordamientos intermedios por potencias grandes.
- Confirmar el orden de los coeficientes antes de escribir ahorra depurar un resultado que "casi" cuadra.
- Leer la entrada completa (dos líneas) es parte del problema, no un detalle.
- En retos de coding, el enunciado suele ser la única especificación: no hay tests visibles más allá del ejemplo.

## Mitigaciones y detección

- No aplica mitigación de seguridad: es un ejercicio de programación.
- Trasladado a producción, la lección es validar rangos y usar enteros de tamaño suficiente.
- Detección: ninguna; no hay componente expuesto.

## Referencias

- <https://www.hackthebox.com/challenges/evaluative>
- <https://7rocky.github.io/en/ctf/htb-challenges/coding/evaluative/>
- <https://tiemenruijgrok.com/posts/2025/07/HTB_Evaluative_Writeup>
- <https://medium.com/@kezosec/evaluative-htb-coding-challenge-writeup-4cbf2661da5a>
