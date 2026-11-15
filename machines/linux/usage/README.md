---
machine: Usage
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, laravel, blind-sqli, laravel-admin, webshell, monit, wildcard, 7z, privesc]
---

# Usage — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un reset de contraseña es vulnerable a SQLi ciega; se dumpea la base y se obtiene el login del admin. Laravel-Admin permite subir un webshell cambiando la extensión después de la validación del cliente, lo que da `dash`. Una contraseña en `.monitrc` funciona para `xander`, que puede ejecutar `usage_management` como root; el script usa `7za` con un wildcard, y un archivo `@lista` más un symlink leen la clave SSH de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nginx con una web Laravel.
- `ffuf` descubre `usage.htb` y `admin.usage.htb`.
- La página de error es la de Laravel y las cookies son `laravel_session`.

## Enumeración

- El formulario de reset de contraseña es vulnerable a SQLi ciega.
- `sqlmap` dumpea la base y recupera el usuario y hash del admin.
- El panel `admin.usage.htb` usa Laravel-Admin.

```bash
sqlmap -r reset.req --batch --dbs
```

## Foothold

Laravel-Admin valida la extensión en el cliente, pero no en el servidor. Se sube una imagen `.php` cambiando la extensión después de la validación y se visita la ruta del avatar para ejecutar el webshell como `dash`.

```text
POST /admin/profile/avatar
filename=shell.php
```

## Movimiento lateral

En el home de `dash`, `.monitrc` contiene una contraseña. Funciona para `xander` con `su` y por SSH.

```bash
cat ~/.monitrc
su - xander
```

## Escalada de privilegios

`xander` puede ejecutar `/usr/bin/usage_management` como root. La opción 1 ejecuta:

```bash
/usr/bin/7za a /var/backups/project.zip -tzip -snl -mmt -- *
```

Se crean `@0xdf` y un symlink `0xdf` a `/root/.ssh/id_rsa`. `7za` interpreta `@0xdf` como lista de archivos y muestra el contenido del symlink en los errores, lo que filtra la clave de root.

```bash
touch @0xdf; ln -fs /root/.ssh/id_rsa 0xdf
sudo usage_management
```

## Evidencia

- SQLi ciega en el reset.
- Laravel-Admin y webshell como `dash`.
- `.monitrc` y `xander`.
- Wildcard de `7za` y clave SSH de root.

## Lecciones aprendidas

- La validación de extensión solo en cliente no protege la subida.
- Una SQLi ciega puede volcar toda la base.
- Los archivos de configuración de Monit guardan credenciales.
- Un wildcard en `7z` con `@lista` filtra archivos.

## Mitigación y detección

- Validar tipo y extensión en el servidor y renombrar archivos.
- Parametrizar consultas y limitar el reset.
- Proteger `.monitrc` y no reutilizar su contraseña.
- Evitar wildcards; usar `find`/`-print0` y rutas absolutas.

## Referencias

- [0xdf — Usage](https://0xdf.gitlab.io/2024/08/10/htb-usage.html)
- [IppSec — Usage](https://www.youtube.com/watch?v=cx9Da-PoXG4)
- [Hack The Box — Usage](https://app.hackthebox.com/machines/usage)
