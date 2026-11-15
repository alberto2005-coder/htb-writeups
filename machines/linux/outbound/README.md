---
machine: Outbound
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, roundcube, cve, privesc]
---

# Outbound — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El webmail Roundcube 1.6.10 es vulnerable a CVE-2025-49113: un objeto PHP serializado en el parámetro `_from` de la subida de avatar ejecuta código y da shell en el contenedor. Desde ahí se descifran las sesiones de Roundcube y se obtiene la contraseña de `jacob`, que reutiliza en SSH. `below` 0.8.0 es vulnerable a CVE-2025-27591: un enlace simbólico en `/var/log/below` permite escribir `/etc/passwd` como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,25,80,443 <IP>
```

- `22` SSH, `25` SMTP, `80/443` nginx con Roundcube.
- La página redirige a `mail.outbound.htb`.
- El webmail muestra la versión 1.6.10.

## Enumeración

- Roundcube permite registrar cuentas y subir un avatar.
- La versión 1.6.10 es anterior a la corrección de CVE-2025-49113.
- El contenedor del webmail tiene la base de datos de Roundcube y las sesiones en `/var/www/html/roundcube/temp/`.

## Foothold

Se genera un objeto PHP con un gadget de Roundcube y se envía base64 en `_from` durante la subida del avatar. El `unserialize` ejecuta el comando y devuelve una reverse shell como `www-data`.

```bash
python3 cve-2025-49113.py --url https://mail.outbound.htb --user <USER> --pass <PASSWORD> --cmd 'id'
```

## Movimiento lateral

Con acceso al contenedor se leen las sesiones de Roundcube. La clave de sesión está en la configuración; al descifrarlas aparecen las credenciales de `jacob`. Esa contraseña también funciona en SSH.

```bash
grep -r des_key /var/www/html/roundcube/config/
php decrypt_session.php <SESSION_FILE>
ssh jacob@<IP>
```

## Escalada de privilegios

`jacob` puede ejecutar `below` como root. La versión 0.8.0 crea `/var/log/below` con permisos de escritura y sigue enlaces simbólicos al rotar logs. Se enlaza `error_root.log` a `/etc/passwd` y se añade un usuario con UID 0 y contraseña conocida.

```bash
ln -sf /etc/passwd /var/log/below/error_root.log
below record
printf '<USER>:<HASH>:0:0:root:/root:/bin/bash\n' >> /etc/passwd
su <USER>
```

## Evidencia

- Versión 1.6.10 y subida de avatar con `_from` serializado.
- Reverse shell en el contenedor de Roundcube.
- Sesiones descifradas y SSH como `jacob`.
- Enlace simbólico de `below` y usuario UID 0 en `/etc/passwd`.

## Lecciones aprendidas

- Un webmail expuesto acumula versiones y configuraciones sensibles.
- Las sesiones cifradas son recuperables si la clave está en el mismo host.
- Un servicio de logs con privilegios y symlinks permite escribir archivos críticos.

## Mitigación y detección

- Actualizar Roundcube y validar parámetros de subida.
- Rotar la `des_key` y no reutilizar contraseñas de aplicación en SSH.
- Actualizar `below` y evitar que siga enlaces en directorios de logs.

## Referencias

- [0xdf — Outbound](https://0xdf.gitlab.io/2025/11/15/htb-outbound.html)
- [IppSec — Outbound](https://www.youtube.com/watch?v=bDql3eTHgZ8)
- [Hack The Box — Outbound](https://app.hackthebox.com/machines/outbound)
