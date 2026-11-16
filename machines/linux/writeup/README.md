---
machine: Writeup
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, cms-made-simple, sqli, path-hijack, run-parts, privesc]
---

# Writeup — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web usa CMS Made Simple anterior a 2.2.10, vulnerable a una SQLi ciega no autenticada. La explotación recupera el salt y el hash de `jkr`, que se crackea y permite SSH. `jkr` está en el grupo `staff`, que puede escribir en `/usr/local/bin`; al iniciar sesión, root ejecuta `run-parts` con ese directorio al principio del PATH, así que un `run-parts` malicioso se ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 7.4 y `80` Apache 2.4.25 en Debian 9.
- La portada es un blog corporativo generado con CMS Made Simple.
- `robots.txt` y `/writeup/` aparecen en la enumeración.

## Enumeración

El generador y la versión se confirman en el HTML. CMS Made Simple < 2.2.10 tiene una SQLi ciega basada en tiempo; se usa un exploit público con `--crack` para extraer el salt, el hash y la contraseña de `jkr`.

## Foothold

La contraseña de `jkr` funciona por SSH. La cuenta pertenece al grupo `staff`; `id` y `ls -ld /usr/local/bin` confirman que el grupo puede escribir ahí.

```bash
# SQLi de CMS Made Simple
python cmsms_sqli.py -u http://<IP>/writeup --crack --wordlist rockyou.txt
# PATH hijack
printf '#!/bin/bash\ncp /bin/bash /tmp/root; chmod 6777 /tmp/root\n' > /usr/local/bin/run-parts
chmod +x /usr/local/bin/run-parts
ssh jkr@<IP>  # dispara run-parts como root
/tmp/root -p
```

## Movimiento lateral

No hay un pivote adicional; la escalada depende de un proceso root que se ejecuta en cada inicio de sesión.

## Escalada de privilegios

`pspy` muestra que al entrar por SSH root ejecuta `/usr/bin/env -i PATH=/usr/local/sbin:/usr/local/bin:... run-parts --lsbsysinit /etc/update-motd.d`. Como `/usr/local/bin` está antes que `/usr/bin` y es escribible por `staff`, se crea un `run-parts` que copia bash y le da SUID. Al volver a entrar por SSH se ejecuta como root.

## Evidencia

- CMS Made Simple < 2.2.10 y SQLi ciega.
- Salt, hash y contraseña de `jkr`.
- Grupo `staff` con escritura en `/usr/local/bin`.
- `run-parts` en el PATH de root y shell SUID.

## Lecciones aprendidas

- Las versiones antiguas de CMS tienen SQLi explotables sin autenticación.
- Un grupo con escritura en el PATH de root es una escalada directa.
- `run-parts` y los scripts de MOTD se ejecutan en cada login.
- `pspy` revela procesos root que no aparecen en `cron`.

## Mitigación y detección

- Actualizar CMS Made Simple y parametrizar consultas.
- Retirar escritura de `staff` en `/usr/local/bin`.
- Usar rutas absolutas en scripts de login.
- Auditar PATH y permisos de directorios de sistema.

## Referencias

- [0xdf — Writeup](https://0xdf.gitlab.io/2019/10/12/htb-writeup.html)
- [IppSec — Writeup](https://www.youtube.com/watch?v=GKq4cwBfH24)
- [Hack The Box — Writeup](https://app.hackthebox.com/machines/writeup)
