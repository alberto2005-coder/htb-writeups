---
machine: Phoenix
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, wordpress, sqli, totp, wildcard]
---

# Phoenix — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

WordPress 5.9 con Asgaros Forum 1.15.35 es vulnerable a una SQLi temporal (CVE-2021-24827). Se extrae el hash de `phoenix`, se crackea y se accede al panel, donde el plugin `download-from-files` permite subir un PHP. El TOTP se salta con una regla PAM que autoriza desde `10.11.12.13`, y un `rsync` con comodín ejecutado por cron da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- `22/tcp` OpenSSH, `80/tcp` redirige a `https://phoenix.htb` y `443/tcp` sirve WordPress.
- `wpscan` identifica WordPress 5.9, el tema `phoenix` y Asgaros Forum 1.15.35.
- El certificado y el vhost confirman `phoenix.htb`.

## Enumeración

- El foro expone `forum.php` y el parámetro `id` del topic.
- La versión de Asgaros es vulnerable a SQLi temporal en `orderby`/`order`.
- `wpscan --enumerate u` lista `phoenix`; el hash está en `wp_users`.

## Foothold

Se confirma la SQLi con `SLEEP(5)` y se extrae el hash de `phoenix` con `sqlmap`. Tras crackearlo, se entra a WordPress y se instala el plugin `download-from-files`, que permite subir un PHP y ejecutarlo.

```bash
sqlmap -u 'https://phoenix.htb/forum/?id=1' --batch --dbs
hashcat -m 400 hash.txt rockyou.txt
# Panel -> Plugins -> download-from-files -> subir shell.php
```

## Movimiento lateral

La shell cae como `www-data`. La base de WordPress contiene el secreto TOTP del usuario y la configuración de PAM está en `/etc/pam.d/`; se lee con el usuario `phoenix` tras obtener su contraseña.

## Escalada de privilegios

`phoenix` tiene un TOTP, pero `/etc/pam.d/access-local.conf` permite `pam_access` sin OTP desde `10.11.12.13`. Se añade esa IP al loopback y se usa `su phoenix`. `sudo -l` muestra un script que ejecuta `rsync` con un comodín; se crea un archivo llamado `--rsh=...` para forzar `-e bash` y ejecutar como root.

```bash
sudo -l
# /usr/bin/rsync -a /home/phoenix/ /opt/backups/
touch -- '--rsh=bash'
```

## Evidencia

- Respuesta retardada por `SLEEP(5)` en Asgaros.
- Hash de `phoenix` crackeado y plugin malicioso instalado.
- `access-local.conf` y archivo `--rsh=bash` en el directorio del backup.

## Lecciones aprendidas

- Un plugin de WordPress con subida de archivos es ejecución remota si se llega al panel.
- Las reglas PAM por IP pueden anular un segundo factor.
- Los comodines en scripts privilegiados permiten inyectar opciones como `--rsh`.

## Mitigación y detección

- Actualizar Asgaros y WordPress; retirar plugins sin mantenimiento.
- No confiar en la IP de origen para saltar MFA; exigir TOTP siempre.
- Evitar comodines con `rsync`/`tar` y usar `--` más listas de archivos.

## Referencias

- [0xdf — Phoenix](https://0xdf.gitlab.io/2022/06/25/htb-phoenix.html)
- [IppSec — Phoenix](https://www.youtube.com/watch?v=Zngo-QzZYtw)
- [Hack The Box — Phoenix](https://app.hackthebox.com/machines/phoenix)
