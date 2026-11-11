---
challenge: Aptitude Test
category: Misc
type: Misc
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [misc, nc, socket, quiz]
---

# Aptitude Test — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un cuestionario por socket: diez preguntas de escenario con cuatro opciones (`A`–`D`). No hay validación de aciertos; cualquier respuesta avanza. Enviando `A` diez veces se llega al final, donde el servicio asigna un rol y devuelve la flag. El «reto» es usar `nc` y no perder la conexión.

## Enunciado y superficie

- Categoría Misc, dificultad Very Easy; Business CTF 2024.
- Solo se da un host y un puerto: no hay binario ni código fuente.
- El enunciado plantea una prueba de aptitud para asignar rol dentro del equipo.

## Reconocimiento

```bash
nc <IP> <PUERTO>
```

El servicio imprime una introducción y la primera pregunta con cuatro opciones. Tras cada respuesta aparece la siguiente; al terminar muestra el rol asignado y la flag.

## Análisis del código

No hay código que analizar. El comportamiento se deduce de la interacción:

- Acepta mayúsculas y minúsculas (`a` y `A` valen).
- No hay temporizador visible ni límite de intentos dentro de la sesión.
- La conexión es lineal: si se cierra, se empieza de nuevo.
- Son diez preguntas, así que no compensa escribir un script.

## Explicación del fallo

No es una vulnerabilidad: es un ejercicio de manejo de sockets. La única «debilidad» es que el resultado no depende de acertar, solo de completar el cuestionario. El servicio está pensado para practicar `nc` y la lectura de prompts.

## Reproducción local

No aplica: el reto es una instancia remota y no se distribuye el servidor. Se puede simular con un script que imprima preguntas y lea respuestas, pero no aporta nada al método.

## Explotación

1. Conectar con `nc <IP> <PUERTO>`.
2. Leer la pregunta y escribir `A` (o `a`) seguido de Intro.
3. Repetir diez veces.
4. Anotar el rol y la flag que imprime el servicio.

Automatización opcional con `pwntools`, útil si se quiere evitar el copia y pega:

```python
from pwn import remote

io = remote("<IP>", <PUERTO>)
for _ in range(10):
    io.recvuntil(b"> ")
    io.sendline(b"A")
print(io.recvall().decode(errors="replace"))
```

El número exacto de preguntas se confirma leyendo la salida; el oficial son diez.

## Evidencia

- Transcripción de las diez preguntas y respuestas.
- Rol asignado y flag al final; se guardan en `private/`.

## Lecciones aprendidas

- **No hace falta acertar**: el cuestionario no puntúa, solo avanza.
- **Conexión lineal**: cerrar `nc` obliga a empezar; conviene tener la terminal estable.
- **Script innecesario**: con diez preguntas, automatizar cuesta más que responder.

## Mitigaciones y detección

- Si un cuestionario real debe evaluar, la puntuación tiene que calcularse en servidor y no aceptar cualquier opción como válida.
- Un servicio de prueba no debería entregar secretos por completar el flujo sin validar respuestas.
- Detección: sesiones que responden siempre la misma opción en todos los ítems; límites de tasa y validación por pregunta.

## Referencias

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BVery%20Easy%5D%20Aptitude%20Test>
- <https://www.kali.org/tools/netcat/>
- <https://docs.pwntools.com/en/stable/remote.html>
