---
machine: Chaos
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, wordpress, webmail, pdftex, rbash, password-reuse, privesc]
---

# Chaos — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La enumeración encuentra WordPress, Webmin y webmail. Unas credenciales débiles dan acceso al correo, donde un mensaje cifrado lleva a una URL secreta con pdfTeX y `\write18` habilitado, lo que da shell como `www-data`. Una contraseña compartida permite pasar a `ayush`, se escapa de `rbash` con `tar` y el perfil de Firefox guarda la contraseña de root, reutilizada también en Webmin.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,110,143,993,995,10000 <IP>
```

- `80` Apache con WordPress en `/wp/wordpress/` y una página principal.
- `10000` Webmin 1.890.
- `110`, `143`, `993` y `995` servicios de correo; el webmail está en un vhost.

## Enumeración

- `gobuster` encuentra `/source` y el WordPress permite enumerar usuarios.
- Una entrada del blog contiene credenciales de webmail.
- El buzón tiene un mensaje cifrado; al descifrarlo aparece una URL secreta.
- `wfuzz` descubre el vhost del webmail y la ruta `J00_w1ll_f1Nd_n07H1n9_H3r3`.

## Foothold

La página secreta compila LaTeX con `pdfTeX` y `\write18` habilitado. El parámetro `content` se pasa al compilador; `\immediate\write18{...}` ejecuta comandos.

```bash
curl -X POST -d 'content=%5Cimmediate%5Cwrite18%7Bid%7D&template=test3' \
  http://chaos.htb/J00_w1ll_f1Nd_n07H1n9_H3r3/ajax.php
```

Con una reverse shell se obtiene `www-data`.

## Movimiento lateral

La contraseña compartida permite `su ayush`. Su shell es `rbash`; `tar` con `--checkpoint-action=exec` o el truco de `tar cf /dev/null` permite escapar.

```bash
tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash
```

## Escalada de privilegios

El perfil de Firefox de `ayush` contiene una contraseña maestra y credenciales guardadas. `firefox_decrypt.py` extrae una contraseña de root; también funciona en Webmin.

```bash
python3 firefox_decrypt.py /home/ayush/.mozilla/firefox
su root
```

## Evidencia

- WordPress, Webmin y webmail expuestos.
- Credenciales débiles y mensaje cifrado.
- pdfTeX con `\write18`.
- `rbash` escapado con `tar`.
- Contraseña de root en Firefox y reutilizada en Webmin.

## Lecciones aprendidas

- Los servicios de correo y webmail amplían la superficie de credenciales.
- `pdfTeX` con `\write18` es ejecución de comandos directa.
- `rbash` no es una jaula si quedan binarios con escape.
- Los perfiles de navegador guardan secretos reutilizables.

## Mitigación y detección

- Deshabilitar `\write18` y compilar en un sandbox sin red.
- No reutilizar contraseñas entre correo, sistema y paneles.
- Restringir `rbash` y auditar binarios con `GTFOBins`.
- Proteger los perfiles de navegador y rotar credenciales compartidas.

## Referencias

- [0xdf — Chaos](https://0xdf.gitlab.io/2019/05/25/htb-chaos.html)
- [IppSec — Chaos](https://www.youtube.com/watch?v=no9UnySBQrU)
- [Hack The Box — Chaos](https://app.hackthebox.com/machines/chaos)
