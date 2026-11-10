---
sherlock: Payload
domain: Análisis de malware
difficulty: Easy
platform: Hack The Box
state: Retired
evidence: Ejecutable de Windows con payload cifrado en runtime
tools: [PEStudio, radare2, x64dbg, Detect It Easy]
tags: [malware, windows, mingw, unpacking, x64dbg]
---

# Payload — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de análisis; sin respuestas literales de la plataforma.

## Escenario

Primer día después del entrenamiento: llega un binario sospechoso y hay que decir qué hace sin ejecutarlo en producción. El ejecutable muestra un diálogo inofensivo y **descifra en memoria** el payload que realmente importa.

## Evidencias

- Un único fichero: **`func_pointer.exe`**.

## Investigación

### 1. Triage estático

```bash
file func_pointer.exe
rabin2 -I func_pointer.exe      # o radare2 -I: arquitectura, bits, protections, timestamp
```

- El binario está compilado con **MinGW** (GCC para Windows): los strings de compilador y la tabla de imports mínima lo delatan.
- Al ejecutarlo sólo aparece un cuadro de diálogo con el texto `HTB pwned us`: la funcionalidad está detrás de una rutina de descifrado.
- El *timestamp* de compilación de la cabecera PE y el compilador son las dos primeras respuestas que se piden.

### 2. Dónde está el payload

El binario usa **punteros a función**: toma un buffer cifrado, lo descifra en memoria y salta a él. En `x64dbg`:

1. Cargar, ejecutar hasta el *entry point* de usuario (`Run to user code`).
2. Buscar la llamada que recibe un buffer y una longitud, y el bucle que escribe byte a byte con `XOR` (o un cifrado de bloque pequeño).
3. Poner un **breakpoint después del bucle**: en ese punto el buffer ya está en claro.

### 3. Extraer el segundo estadio

```text
Follow in Dump → seleccionar la región → Binary → Save to file
```

El volcado contiene el payload descifrado. El reto pide **la dirección** donde quedó y el contenido: con `strings` sobre el volcado aparecen la URL de C2, el nombre del servicio o los comandos.

### 4. Verificación

- `PEStudio` sobre el volcado confirma si es un PE completo o shellcode.
- Comparar el hash del fichero original con el del volcado: deben ser distintos (uno cifrado, otro en claro).

## Conclusiones

- El binario es un *loader*: no ataca por sí mismo, entrega el siguiente estadio.
- El cifrado es reversible **en el propio host**; no hace falta reimplementar el algoritmo.
- La dirección del buffer descifrado es un dato del análisis, no un detalle interno.

## Lecciones

- Ante un *packer* casero, el depurador hace el trabajo: ejecutar hasta que el malware se descifre a sí mismo.
- `MinGW` + imports mínimos + diálogo señuelo es un perfil de loader, no de aplicación.
- El *timestamp* de la cabecera PE no es fiable como prueba de compilación, pero sí como pista.
- Nunca lanzar el segundo estadio fuera de una VM aislada y sin red.
