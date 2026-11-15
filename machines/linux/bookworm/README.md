---
machine: Bookworm
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, xss, idor, express, symlink, postscript, sqli, privesc]
---

# Bookworm — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un XSS en las notas de un pedido, la subida de avatar y un IDOR permiten descargar un ZIP con traversal y leer el código y las credenciales de la base. Esas credenciales funcionan por SSH para `frank`, que accede al servidor de conversión de ebooks de `neil`; un symlink escribe una clave SSH en su home. Como `neil`, `genlabel` se ejecuta como root y una SQLi inyecta PostScript en `ps2pdf -dNOSAFER`, lo que permite escribir en `/root/.ssh/authorized_keys`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nginx con redirección a `bookworm.htb`.
- La aplicación es Express/Node con login, tienda, perfil y descarga de pedidos.
- `feroxbuster` encuentra `/login`, `/register`, `/shop`, `/profile`, `/basket` y `/static`.

## Enumeración

- El campo de notas del pedido refleja HTML y permite XSS; el CSP no impide exfiltrar datos.
- La subida de avatar devuelve un ID numérico y el perfil lo referencia sin comprobar el propietario (IDOR).
- La descarga de varios libros genera un ZIP; un `bookIds` manipulado incluye `../../etc/passwd` y `database.js`.

```text
bookIds=1,2,../../../../var/www/bookworm/database.js
```

## Foothold

`database.js` contiene las credenciales de MySQL. La misma contraseña funciona por SSH para `frank`.

```bash
ssh frank@bookworm.htb
```

## Movimiento lateral

`frank` puede leer `/home/neil`, donde corre un conversor de ebooks en el puerto 3001. La aplicación acepta un archivo y lo procesa con Calibre; se sube un symlink a `/home/neil/.ssh/authorized_keys` y se consigue escritura como `neil`.

```bash
ln -s /home/neil/.ssh/authorized_keys payload
```

## Escalada de privilegios

`neil` puede ejecutar `/usr/local/bin/genlabel` como root. El script consulta la base y genera un `.ps`; una SQLi controla el contenido y `ps2pdf` se lanza con `-dNOSAFER`. PostScript permite leer y escribir archivos como root.

```bash
sudo genlabel '99999 UNION SELECT "x) /outfile (/root/.ssh/authorized_keys) (w) file def ...";'
```

También se puede leer `/root/.ssh/id_ed25519` con `(r) file`.

## Evidencia

- XSS, subida y IDOR en la tienda.
- ZIP con traversal y `database.js`.
- Credenciales de `frank` y servidor de `neil`.
- Symlink a `authorized_keys`.
- SQLi/PostScript en `genlabel` y root.

## Lecciones aprendidas

- Encadenar XSS, subida e IDOR convierte funciones menores en una fuga completa.
- Un ZIP que acepta rutas relativas es lectura arbitraria.
- Los servicios internos de conversión suelen escribir con los permisos del usuario.
- `ps2pdf` con `-dNOSAFER` convierte PostScript en lectura/escritura arbitraria.

## Mitigación y detección

- Validar el propietario en cada descarga y normalizar rutas dentro del ZIP.
- No reutilizar credenciales de base para SSH.
- Ejecutar conversores en un sandbox sin acceso a `.ssh`.
- No usar `-dNOSAFER`; aplicar `policy.xml` y revisar los `.ps` generados.

## Referencias

- [0xdf — Bookworm](https://0xdf.gitlab.io/2024/01/20/htb-bookworm.html)
- [IppSec — Bookworm](https://www.youtube.com/watch?v=UqDdR10F54A)
- [Hack The Box — Bookworm](https://app.hackthebox.com/machines/bookworm)
