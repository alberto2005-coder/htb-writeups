---
challenge: Nombre
category: Challenge
type: web
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
solved: YYYY-MM-DD
points: 0
tags: [web, php, pwn]
---

# Nombre — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired / Active (borrador privado).
> Las flags reales están en `private/` y no se publican.

## TL;DR

Qué es el reto, dónde está el fallo y qué se consigue, en 3–5 líneas.

## Enunciado y superficie

- Categoría y dificultad.
- Qué entrega el reto (código, binario, contenedor, URL).
- Pistas del enunciado.

## Reconocimiento

```bash
curl -s -I http://<IP>:<puerto>/
```

- Cabeceras y tecnologías.
- Versiones exactas (las que fijan los offsets o el CVE).
- Qué no hay (endpoints, parámetros, formularios).

## Análisis del código

- Ficheros relevantes y configuración por defecto.
- Línea o función vulnerable.
- Por qué el fallo es alcanzable sin autenticación.

## Explicación del fallo

Describe el mecanismo (memory corruption, cripto, lógica...) con el nivel de detalle necesario para reproducirlo. Diagramas en ASCII si ayudan.

## Reproducción local

```bash
# build/run del contenedor o del binario
```

- Cómo se depura (gdb, breakpoints, símbolos).
- Offsets o constantes dependientes del build y cómo se obtienen.

## Explotación

```bash
python3 exploit.py --url http://<IP>:<puerto>/
```

- Cadena paso a paso.
- Salida que confirma la ejecución.
- Limitaciones (tamaño de payload, ASLR, workers, red saliente).

## Evidencia

- Salida recortada, sin flags ni tokens.

## Lecciones aprendidas

- Qué se intentó y no funcionó.
- Errores del script o del entorno.
- Qué harías distinto.

## Mitigaciones y detección

- Versión corregida o configuración segura.
- Reglas de detección (WAF, logs, límites de subida).
- Referencias (CVE, MITRE ATT&CK).

## Referencias

- ...
