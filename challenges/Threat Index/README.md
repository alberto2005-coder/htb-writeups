---
challenge: Threat Index
category: Challenge
type: coding
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [coding, python, string-matching, weighted-score, stdin-stdout]
---

# Threat Index — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Hay que puntuar una cadena de tráfico simulado sumando, por cada palabra clave, sus apariciones multiplicadas por un peso fijo (de 1 a 18). Sin binario ni servicio: se resuelve recorriendo un diccionario de 18 términos y contando ocurrencias. La única decisión es si el conteo debe ser solapado o no; con estas palabras, no hay diferencia.

## Enunciado y superficie

- Categoría **Coding**, dificultad **Very Easy**.
- Editor en la plataforma (C, C++, Python o Rust), sin ficheros adjuntos.
- Entrada: una cadena de minúsculas y dígitos, longitud entre 30 y 10⁶.
- Salida: `Σ (apariciones × peso)`.

| Peso | Palabra | Peso | Palabra |
|---:|---|---:|---|
| 1 | `scan` | 10 | `inject` |
| 2 | `response` | 11 | `execute` |
| 3 | `control` | 12 | `deploy` |
| 4 | `callback` | 13 | `malware` |
| 5 | `implant` | 14 | `exploit` |
| 6 | `zombie` | 15 | `payload` |
| 7 | `trigger` | 16 | `backdoor` |
| 8 | `infected` | 17 | `zeroday` |
| 9 | `compromise` | 18 | `botnet` |

```text
Entrada
payloadrandompayloadhtbzerodayrandombytesmalware

Salida
60
```

(`payload` dos veces × 15 = 30, `zeroday` 17, `malware` 13.)

## Reconocimiento

- La cadena solo tiene minúsculas y dígitos, así que no hay que normalizar mayúsculas.
- Los términos no se solapan entre sí en la práctica; `count` de Python es suficiente.
- La longitud llega a 10⁶: conviene recorrer la cadena una vez por palabra (18 pasadas) y no generar subcadenas.

## Análisis del código

```python
weights = {
    "scan": 1, "response": 2, "control": 3, "callback": 4,
    "implant": 5, "zombie": 6, "trigger": 7, "infected": 8,
    "compromise": 9, "inject": 10, "execute": 11, "deploy": 12,
    "malware": 13, "exploit": 14, "payload": 15, "backdoor": 16,
    "zeroday": 17, "botnet": 18,
}

stream = input().strip()
print(sum(stream.count(k) * w for k, w in weights.items()))
```

La complejidad es `O(18 · n)`, aceptable para 10⁶. Un autómata tipo Aho-Corasick sería más rápido, pero innecesario.

## Explicación del fallo

No hay vulnerabilidad; el ejercicio mide implementar una suma ponderada sin equivocar los pesos. Los errores típicos son confundir el peso con la posición, olvidar una palabra o contar con `str.count` sobre una cadena que ya se ha consumido.

## Reproducción local

```bash
printf '%s\n' 'payloadrandompayloadhtbzerodayrandombytesmalware' | python3 threat_index.py
# 60
```

## Explotación

1. Leer la cadena completa con `input().strip()`.
2. Recorrer el diccionario y sumar `count × peso`.
3. Enviar la solución; la plataforma valida el resultado.

## Evidencia

- Salida local `60` con el ejemplo del enunciado.
- Sin flag real en la ficha.

## Lecciones aprendidas

- Leer el enunciado con la tabla delante evita inventar pesos.
- `str.count` cuenta subcadenas no solapadas; si los términos pudieran solaparse, haría falta otro enfoque.
- Con entradas de un millón de caracteres, medir antes de optimizar: 18 pasadas son baratas.

## Mitigaciones y detección

- No aplica mitigación de seguridad.
- En un sistema real, el equivalente sería un motor de reglas con pesos versionados y límites de tamaño de entrada.

## Referencias

- <https://www.hackthebox.com/challenges/threat-index>
- <https://chrispham-cyber.github.io/posts/Threat-Index/>
- <https://motasem-notes.net/practical-coding-in-cyber-security-hackthebox-coding-challenges>
- <https://7rocky.github.io/en/ctf/htb-challenges/coding/>
