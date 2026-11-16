---
machine: Developer
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, django, reverse-tabnabbing, pickle, postgresql, privesc]
---

# Developer — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La plataforma de retos permite enviar un enlace de writeup que el admin visita. Un ataque de reverse tab-nabbing redirige la pestaña original a un login falso y captura las credenciales del admin, que sirven para Django admin y Sentry. Sentry filtra la `SECRET_KEY` en modo debug; con ella se firma una cookie pickle y se ejecuta código como `www-data`. Los hashes de PostgreSQL llevan a `karl`, y un binario con sudo revela la contraseña de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con una plataforma tipo CTF.
- Registro, login, reset de contraseña y envío de writeups.
- Ocho retos de cuatro categorías; el admin revisa los enlaces enviados.

## Enumeración

El perfil permite enviar una URL de writeup. El enlace se abre con `target="_blank"` y sin `rel=noopener`, así que la página nueva puede cambiar `window.opener.location`. Se aloja una página que redirige la pestaña original a un login clonado y registra el POST.

## Foothold

El admin introduce sus credenciales en el login falso. Con ellas se entra en `/admin` y en Sentry. Al provocar un error, Django muestra el debug y la `SECRET_KEY`. Se firma una cookie de sesión con `PickleSerializer` que ejecuta una reverse shell y se obtiene `www-data`.

```bash
# reverse tab-nabbing
<script>window.opener.location='http://<ATTACKER>/login';</script>
# cookie pickle con la SECRET_KEY filtrada
python2 django_pickle.py '<CMD>'
# crack del hash de Django
hashcat -m 10000 karl.hash rockyou.txt
```

## Movimiento lateral

En `/home/mark/developer_ctf` hay credenciales de PostgreSQL. Se enumeran las bases `platform` y `sentry`; el hash PBKDF2 de `karl` se crackea y su contraseña funciona por SSH.

## Escalada de privilegios

`karl` puede ejecutar con sudo un binario que pide una contraseña, la cifra con una clave e IV estáticos y la compara con bytes embebidos. Al revertir el binario se obtienen la clave y el IV, se descifra el valor esperado y se introduce; el programa pide una clave pública SSH y la instala para root.

## Evidencia

- Enlace de writeup sin `noopener`.
- Credenciales del admin capturadas.
- `SECRET_KEY` en el debug de Sentry.
- Cookie pickle y shell `www-data`.
- Hash de `karl` y binario con sudo.

## Lecciones aprendidas

- `target="_blank"` sin `noopener` permite reverse tab-nabbing.
- El modo debug expone secretos de firma.
- Una `SECRET_KEY` de Django con cookies pickle equivale a RCE.
- Los binarios que comparan secretos embebidos se pueden revertir.

## Mitigación y detección

- Añadir `rel="noopener noreferrer"` a enlaces externos.
- Desactivar debug y rotar `SECRET_KEY`.
- No usar `PickleSerializer` para sesiones.
- Revisar binarios con sudo y no incrustar contraseñas.

## Referencias

- [0xdf — Developer](https://0xdf.gitlab.io/2022/01/15/htb-developer.html)
- [IppSec — Developer](https://www.youtube.com/watch?v=MjkDCy10BYM)
- [Hack The Box — Developer](https://app.hackthebox.com/machines/developer)
