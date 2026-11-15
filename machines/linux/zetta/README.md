---
machine: Zetta
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, ftp, rsync, postgres, sqli, privesc]
---

# Zetta — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Pure-FTPd acepta cualquier usuario y contraseña de 32 caracteres; con FXP se descubre una dirección IPv6 y rsync en 8730 expone `/etc`. Se lee la configuración de rsyslog y se obtiene `roy`; rsync permite escribir su `authorized_keys`. La plantilla de rsyslog inserta el mensaje en PostgreSQL, lo que da SQLi con consultas apiladas: se escribe una clave de `postgres` y se lee `.psql_history`, que revela el esquema de contraseñas y permite `su root`.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80,8730 <IP>
```

- `21` Pure-FTPd, `22` SSH, `80` HTTP y `8730` rsync.
- El FTP anuncia `AUTH TLS` y acepta usuarios de 32 caracteres.
- El puerto 8730 responde al módulo rsync.

## Enumeración

- Cualquier usuario y contraseña de 32 caracteres idénticos se autentica; el home es `/srv/ftp/home/<USER>`.
- `PRET EPRT`/`PORT` permite un FTP bounce; con `EPRT` se descubre una IPv6 y un servicio rsync interno.
- `rsync rsync://<IP>:8730/` lista módulos y `/etc` es legible.

## Foothold

Se descarga `/etc/rsyslog.conf` y `/etc/rsyslog.d/*.conf`. La configuración contiene credenciales de `roy`; además, rsync permite subir un `authorized_keys` a `home_roy`. Se entra por SSH como `roy`.

```bash
rsync rsync://<IP>:8730/etc/rsyslog.d/ /tmp/rsyslog/
rsync /tmp/authorized_keys rsync://<IP>:8730/home_roy/.ssh/authorized_keys
ssh -i id_rsa roy@<IP>
```

## Movimiento lateral

La configuración de rsyslog usa `ompgsql` con `postgres` y una plantilla SQL. `roy` está en `adm` y puede leer `/var/log/postgresql`, así que se prueba inyección con `logger`.

```bash
logger -p local7.info "test', null)-- -"
```

## Escalada de privilegios

La inyección acepta consultas apiladas. Se crea una tabla, se inserta una clave pública y se escribe en `/var/lib/postgresql/.ssh/authorized_keys` con `COPY ... TO`. Después se lee `.psql_history`, que contiene una contraseña de PostgreSQL; el esquema añade `@root` para `su`, y se obtiene root.

```bash
logger -p local7.info "sd',null); CREATE TABLE aaa (c text); INSERT INTO aaa VALUES (\\$$<PUBKEY>\\$$); COPY (SELECT * FROM aaa) TO \\$$/var/lib/postgresql/.ssh/authorized_keys\\$$;-- -"
```

## Evidencia

- FTP con autenticación de 32 caracteres y bounce EPRT.
- rsync en 8730 con `/etc` y `home_roy` escribible.
- Plantilla de rsyslog y SQLi con `logger`.
- `COPY TO` escribiendo la clave de `postgres` y `su root`.

## Lecciones aprendidas

- Un servidor FTP con autenticación débil puede servir de pivote a IPv6.
- rsync sin restricciones permite leer configuración y escribir claves.
- Una plantilla SQL de logs es una entrada directa a la base de datos.

## Mitigación y detección

- Requerir autenticación real y deshabilitar FXP.
- Restringir módulos rsync y permisos de escritura.
- Parametrizar la plantilla de rsyslog y limitar `COPY ... PROGRAM`.

## Referencias

- [0xdf — Zetta](https://0xdf.gitlab.io/2020/02/22/htb-zetta.html)
- [IppSec — Zetta](https://www.youtube.com/watch?v=8XmTz3A5rUo)
- [Hack The Box — Zetta](https://app.hackthebox.com/machines/zetta)
