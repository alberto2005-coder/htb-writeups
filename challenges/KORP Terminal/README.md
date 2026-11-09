---
challenge: KORP Terminal
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, bcrypt, sqlmap, cyber-apocalypse-2024]
type: Web
---


# KORP Terminal — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un login de una terminal ficticia. Una comilla simple provoca un **error de MySQL**: hay **SQL injection**. La aplicación responde **401** aunque el error se muestre, así que `sqlmap` hay que lanzarlo con `--ignore-code 401`. Se vuelca la tabla `users`, se crackea el hash **bcrypt** y se entra como `admin`.

## Enunciado y superficie

- Categoría Web; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Un login de una terminal ficticia. Una comilla simple provoca un **error de MySQL**: hay **SQL injection**. La aplicación responde **401** aunque el error se muestre, así que `sqlmap` hay que lanzarlo con `--ignore-code 401`. Se vuelca la tabla `users`, se crackea el hash **bcrypt** y se entra como `admin`.

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- Una instancia web con un formulario de usuario/contraseña.

## Lecciones aprendidas

- **`--ignore-code 401`**: sin ese flag, `sqlmap` abandona al considerar el *endpoint* inaccesible.
- **`-r` con la petición completa**: conservar cabeceras y método POST; la inyección va en el cuerpo.
- **bcrypt es lento**: pocas palabras por segundo; usar solo diccionarios razonables.

- Un error de base de datos visible en producción es un mapa para el atacante.
- Un código de estado engañoso no detiene la inyección: la respuesta sigue siendo válida.
- Contraseñas con bcrypt siguen cayendo si son débiles.

## Mitigaciones y detección

- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)

## Método

1. **Confirmar la inyección**: `'` en usuario y en contraseña; el error SQL aparece en la respuesta.

2. **Automatizar ignorando el 401**:

```bash
sqlmap -r login.req --batch --ignore-code 401 --dbs
sqlmap -r login.req --batch --ignore-code 401 -D korp_terminal --tables
sqlmap -r login.req --batch --ignore-code 401 -D korp_terminal -T users --dump
```

3. **Crackear el bcrypt**:

```bash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
# o: hashcat -m 3200
```

4. **Entrar** con las credenciales recuperadas: la respuesta trae la flag.
