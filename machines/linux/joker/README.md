---
machine: Joker
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, squid, tftp, werkzeug, udp, sudoedit, tar, wildcard, privesc]
---

# Joker — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

TFTP permite descargar la configuración de Squid y el archivo de contraseñas del proxy. Con esas credenciales se accede a un servidor Werkzeug en localhost que ofrece una consola Python; el firewall bloquea TCP saliente pero permite UDP, así que se usa una reverse shell UDP. Una regla de sudoedit con wildcard lleva a `alekos`, y un cron que ejecuta `tar` con `*` permite inyectar opciones y obtener root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,3128 <IP>
nmap -sU -p69 <IP>
```

- `22` SSH y `3128` Squid 3.5.12.
- TFTP en UDP `69`.
- Squid responde `407 Proxy Authentication Required` y revela el realm `kalamari`.

## Enumeración

TFTP no lista directorios, pero se descargan `/etc/squid/squid.conf` y `/etc/squid/passwords`. El hash `$apr1$` se crackea con hashcat modo 1600. Con el proxy autenticado se escanea `127.0.0.1` y se encuentra un Werkzeug en el puerto 8080.

## Foothold

La consola de Werkzeug permite ejecutar Python. Al intentar una reverse shell TCP no hay conectividad saliente; se enumera el firewall y se usa una reverse shell UDP con `socat file:/dev/pts/0,raw,echo=0 udp-listen:<PORT>`. La sesión queda como `werkzeug`.

```bash
# TFTP
tftp <IP>
tftp> get /etc/squid/squid.conf
tftp> get /etc/squid/passwords
# proxy a localhost
curl -x http://<USER>:<PASS>@<IP>:3128 http://127.0.0.1:8080/
# tar wildcard
touch -- '--checkpoint=1' '--checkpoint-action=exec=/dev/shm/root.sh'
```

## Movimiento lateral

`werkzeug` puede ejecutar `sudoedit /var/www/*/*/layout.html`. Se crea un directorio y un symlink `layout.html` hacia `/home/alekos/.ssh/authorized_keys`; `sudoedit` sigue el enlace y permite insertar una clave pública. También funciona el abuso de wildcard para editar el archivo directamente.

## Escalada de privilegios

Un cron root hace `cd /home/alekos/development` y `tar cf /home/alekos/backup/$FILENAME *`. Se crean archivos llamados `--checkpoint=1` y `--checkpoint-action=exec=<script>`; el wildcard los expande como opciones de `tar` y el script se ejecuta como root.

## Evidencia

- Configuración y hash de Squid por TFTP.
- Proxy autenticado y consola Werkzeug.
- Reverse shell UDP.
- `sudoedit` con symlink/wildcard.
- `tar` con wildcard como root.

## Lecciones aprendidas

- TFTP permite leer archivos si se conoce la ruta.
- Un proxy autenticado puede exponer servicios en localhost.
- Las reglas `sudoedit` con wildcard son peligrosas.
- Los wildcards en `tar` permiten inyectar opciones.

## Mitigación y detección

- Restringir TFTP y no almacenar hashes en rutas legibles.
- Limitar el proxy a destinos necesarios.
- Evitar wildcards en sudoedit; usar rutas absolutas y `--`.
- Usar `find -print0`/`xargs -0` en backups.

## Referencias

- [0xdf — Joker](https://0xdf.gitlab.io/2020/08/13/htb-joker.html)
- [IppSec — Joker](https://www.youtube.com/watch?v=5wyvpJa9LdU)
- [Hack The Box — Joker](https://app.hackthebox.com/machines/joker)
