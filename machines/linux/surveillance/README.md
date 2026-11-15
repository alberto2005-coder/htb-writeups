---
machine: Surveillance
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, craftcms, zoneminder, cve, privesc]
---

# Surveillance — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Craft CMS 4.4.14 es vulnerable a CVE-2023-41892 y permite ejecutar código sin autenticación. Un backup SQL expone el hash SHA-256 de `matthew`, que se crackea para entrar por SSH. ZoneMinder 1.36.32 tiene CVE-2023-26035 y un script de actualización ejecutado con `sudo` que permite inyectar comandos.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 22.04 y `80/tcp` nginx con `surveillance.htb`.
- La web usa Craft CMS y redirige a `/admin` para el panel.
- El pie de página y `/admin/login` confirman Craft CMS 4.4.14.

## Enumeración

- `CVE-2023-41892` abusa de `conditions` en una petición a `actions/conditions/render` para instanciar objetos y ejecutar PHP.
- El exploit público devuelve un webshell en `/tmp` o ejecuta comandos directamente.
- En el sistema hay un backup `backup.sql` con la tabla de usuarios de Craft.

## Foothold

Se usa el exploit de Craft para ejecutar una reverse shell como `www-data`. Después se localiza `backup.sql`, se extrae el hash SHA-256 de `matthew` y se crackea con `hashcat -m 1400`.

```bash
python3 CVE-2023-41892.py http://<IP>
# shell como www-data
find / -name backup.sql 2>/dev/null
hashcat -m 1400 hash.txt rockyou.txt
ssh matthew@<IP>
```

## Movimiento lateral

`matthew` tiene acceso SSH y puede enumerar los servicios locales. ZoneMinder escucha en `localhost:8080`; sus credenciales y la configuración del sistema quedan al alcance del usuario.

## Escalada de privilegios

`sudo -l` permite ejecutar `/usr/bin/zm*.pl` como root. ZoneMinder 1.36.32 es vulnerable a CVE-2023-26035 y su script `zmupdate.pl` pasa parámetros a una shell; se inyecta un comando o se usa `LD_PRELOAD` con una biblioteca propia para ejecutar código como root.

```bash
sudo -l
sudo /usr/bin/zmupdate.pl --user='; /bin/bash #'
# Alternativa: sudo LD_PRELOAD=/tmp/pwn.so /usr/bin/zmupdate.pl
```

## Evidencia

- Ejecución de PHP sin autenticación en Craft CMS.
- Hash SHA-256 de `matthew` crackeado.
- `sudo -l` con `zm*.pl` y shell de root.

## Lecciones aprendidas

- Un CMS desactualizado puede dar ejecución sin credenciales.
- Los backups de bases de datos suelen contener hashes crackeables.
- Un script de mantenimiento con `sudo` y parámetros sin sanear es ejecución root.

## Mitigación y detección

- Actualizar Craft CMS y ZoneMinder a versiones corregidas.
- Restringir backups y cifrarlos; no dejarlos en el webroot.
- Evitar `sudo` sobre scripts que acepten parámetros y usar `env_reset`.

## Referencias

- [0xdf — Surveillance](https://0xdf.gitlab.io/2024/04/20/htb-surveillance.html)
- [IppSec — Surveillance](https://www.youtube.com/watch?v=HMC5WZH3o-E)
- [Hack The Box — Surveillance](https://app.hackthebox.com/machines/surveillance)
