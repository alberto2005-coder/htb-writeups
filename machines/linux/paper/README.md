---
machine: Paper
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, wordpress, rocket-chat, cve-2019-17671, polkit]
---

# Paper — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un borrador privado de WordPress se filtra con `?static=1` y contiene credenciales de Rocket.Chat. La versión vulnerable de Rocket.Chat permite leer mensajes/archivos y obtener acceso; la escalada final usa polkit (CVE-2021-3560).

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,443 <IP>
```

Se añaden `paper.htb` y `office.paper.htb` al hosts. WordPress corre en el vhost de oficina; se enumera con `wpscan` y `feroxbuster`.

## Acceso inicial

El WordPress expone un borrador no publicado mediante el parámetro `static`:

```bash
curl 'http://office.paper.htb/?static=1'
```

El contenido incluye credenciales de Rocket.Chat. Se inicia sesión en `chat.paper.htb` y se enumeran canales y usuarios. La versión de Rocket.Chat es vulnerable a CVE-2019-17671 (lectura no autorizada de mensajes/archivos). Se localiza una contraseña de SSH en un mensaje y se accede como `dwight`.

## Movimiento lateral

```bash
ssh dwight@paper.htb
```

Se revisan procesos, tareas y credenciales locales. Se identifica la versión de polkit y se prepara la escalada.

## Escalada a root

Polkit 0.105-25 es vulnerable a CVE-2021-3560. Se crea un usuario administrador aprovechando la carrera en la comprobación de identidad:

```bash
time ./poc.sh
```

El script crea un usuario con UID 0 o añade privilegios; después se usa `su` para obtener root. También puede explotarse manualmente con `dbus-send` y una carrera.

## Evidencia

- Borrador de WordPress filtrado.
- Sesión de Rocket.Chat y mensaje con credencial redactada.
- Acceso SSH como `dwight`.
- `pkexec --version` y salida del PoC (redactada).

## Lecciones aprendidas

- Los borradores de WordPress pueden ser accesibles con parámetros de vista previa.
- Rocket.Chat debe actualizarse y restringir la lectura de mensajes.
- Las credenciales en chats se reutilizan en SSH.
- Polkit antiguo permite escalada local fiable.

## Mitigación y detección

- Restringir vistas previas y borradores a usuarios autenticados.
- Actualizar Rocket.Chat y WordPress.
- No compartir credenciales por chat.
- Actualizar polkit y monitorizar creación de usuarios inesperados.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2019-17671>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-3560>
- <https://www.hackthebox.com/machines/paper>
