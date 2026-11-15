---
machine: Unattended
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, nginx-alias, lfi, session-poisoning, initrd, privesc]
---

# Unattended — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una SQLi ciega en `index.php?id=` es lenta de volcar; un alias de nginx sin slash (`dev../html/index.php`) filtra el código fuente. La SQLi se convierte en LFI, se envenena una sesión PHP y se obtiene `www-data`. La tabla `checkrelease` ejecuta comandos y da `guly`; el grupo `grub` permite leer el initrd, cuyo `uinitrd` genera la contraseña de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,443 <IP>
```

- `80`/`443` nginx 1.10.3 con `nestedflanders.htb` y `www.nestedflanders.htb`.
- `index.php?id=` carga páginas por ID.
- `gobuster` encuentra `/dev`, `/html` y rutas de assets.

## Enumeración

`id=587'` devuelve la página principal y `id=587' and 1=1-- -` devuelve la página 587: hay SQLi ciega. Volcar la base es lento. Un alias de nginx mal configurado permite salir del directorio:

```bash
curl -s -k https://www.nestedflanders.htb/dev../html/index.php
```

El código fuente revela la consulta y la ruta de inclusión.

## Foothold

La SQLi permite controlar el archivo incluido. Se escribe una webshell PHP en una cookie, se localiza el archivo de sesión (`/var/lib/php/sessions/sess_<ID>`) y se incluye para ejecutar como `www-data`.

```text
?op=/var/lib/php/sessions/sess_<PHPSESSID>
```

## Movimiento lateral

Las credenciales de MySQL están en el código. La tabla de configuración contiene `checkrelease` con una lista de scripts; se inyecta un comando y se obtiene `guly`.

```sql
UPDATE config SET value='/home/guly/checkbase.pl;bash -c "..."' WHERE name='checkrelease';
```

## Escalada de privilegios

`guly` pertenece al grupo `grub` y puede leer `/boot/initrd.img-4.9.0-8-amd64`. Se descomprime con `zcat` y `cpio`; el script `scripts/local-top/cryptroot` llama a `/sbin/uinitrd` con una cadena fija. Al ejecutarlo se obtiene la contraseña de root.

```bash
zcat /boot/initrd.img-4.9.0-8-amd64 | cpio -idm
./sbin/uinitrd c0m3s3f0ss34nt4n1
su root
```

## Evidencia

- SQLi ciega en `id`.
- Alias nginx y código fuente.
- LFI/session poisoning y `www-data`.
- `checkrelease` y `guly`.
- initrd, `uinitrd` y root.

## Lecciones aprendidas

- Una SQLi lenta puede tener una vía más rápida por configuración del servidor.
- Un alias de nginx sin slash permite traversal.
- Los archivos de sesión PHP son un objetivo de inclusión.
- Las tablas de configuración pueden ejecutar comandos.
- Un initrd legible puede contener la contraseña de root.

## Mitigación y detección

- Parametrizar consultas y usar listas blancas.
- Corregir aliases de nginx y bloquear traversal.
- Guardar sesiones fuera del webroot y escapar cookies.
- No ejecutar comandos desde la base.
- Restringir lectura de `/boot` y proteger initrd.

## Referencias

- [0xdf — Unattended](https://0xdf.gitlab.io/2019/08/24/htb-unattended.html)
- [IppSec — Unattended](https://www.youtube.com/watch?v=2SATzCQY0Zw)
- [Hack The Box — Unattended](https://app.hackthebox.com/machines/unattended)
