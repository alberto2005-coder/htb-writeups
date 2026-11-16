---
machine: Passage
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, cutenews, file-upload, hash, ssh, usbcreator, dbus, privesc]
---

# Passage — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

CuteNews 2.1.2 permite subir un avatar PHP con una webshell en el comentario EXIF. Los usuarios se guardan en archivos base64 dentro de `cdata/users`; al decodificarlos se obtienen hashes SHA-256, uno de ellos de `paul`. Su clave SSH también autentica a `nadav`, que está en el grupo sudo pero no conoce su contraseña; USBCreator permite escribir archivos arbitrarios como root sin contraseña.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 7.2 y `80` Apache en Ubuntu 16.04.
- La web es un blog con un enlace RSS a `/CuteNews/rss.php`.
- El RSS revela CuteNews 2.1.2.

## Enumeración

Se busca la versión en Exploit-DB: hay una subida arbitraria autenticada. Se registra una cuenta, se crea un PNG con `exiftool -Comment='<?php system($_GET["cmd"]); ?>'` y se sube como avatar con extensión `.php`. La webshell queda en `/CuteNews/uploads/avatar_<user>_avatar.php`.

## Foothold

La webshell ejecuta como `www-data`. En `cdata/users` cada usuario es un archivo PHP con una línea base64; al decodificar todas las líneas se extraen correos y hashes SHA-256. El hash de `paul` se crackea y permite `su paul`.

```bash
# webshell en avatar
 exiftool -Comment='<?php system($_GET["cmd"]); ?>' avatar.png
# USBCreator
gdbus call --system --dest com.ubuntu.USBCreator \
  --object-path /com/ubuntu/USBCreator \
  --method com.ubuntu.USBCreator.Image /dev/shm/passwd /etc/passwd true```

## Movimiento lateral

`/home/paul/.ssh` contiene un par de claves; la pública también está en `authorized_keys` de `nadav`. La clave privada permite SSH como `nadav`, que pertenece al grupo sudo.

## Escalada de privilegios

`nadav` no sabe su contraseña, pero el servicio D-Bus `com.ubuntu.USBCreator` permite `Image` para copiar archivos como root sin autenticación. Se copia una versión modificada de `/etc/passwd` con un usuario sin contraseña o se sobrescribe `/etc/shadow`; después `su` da root.

## Evidencia

- CuteNews 2.1.2 y avatar PHP.
- Archivos base64 con hashes en `cdata/users`.
- Hash de `paul` y clave SSH compartida con `nadav`.
- USBCreator y escritura arbitraria como root.

## Lecciones aprendidas

- Los CMS antiguos guardan usuarios en archivos planos codificados.
- Una extensión `.php` en una subida de imagen puede ejecutarse.
- Las claves SSH se reutilizan entre cuentas.
- Un servicio D-Bus privilegiado puede saltar la política de sudo.

## Mitigación y detección

- Actualizar CuteNews y validar tipo/contenido de archivos.
- Guardar usuarios en base de datos y usar bcrypt/Argon2.
- Rotar claves SSH y limitar `authorized_keys`.
- Deshabilitar USBCreator o restringir su interfaz D-Bus.

## Referencias

- [0xdf — Passage](https://0xdf.gitlab.io/2021/03/06/htb-passage.html)
- [IppSec — Passage](https://www.youtube.com/watch?v=kbw4_4jUP_U)
- [Hack The Box — Passage](https://app.hackthebox.com/machines/passage)
