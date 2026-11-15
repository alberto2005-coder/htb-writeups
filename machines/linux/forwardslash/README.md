---
machine: ForwardSlash
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, lfi, xxe, crypto, luks, ssh]
---

# ForwardSlash — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El vhost `backup` incluye una página con inclusión de archivos y un formulario XML vulnerable a XXE. Con el LFI se leen el código y las credenciales de `chiv`; un binario de backup mal configurado permite leer archivos de `pain`. La escalada rompe un cifrado casero, abre un volumen LUKS y recupera la clave SSH de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 18.04 y `80/tcp` Apache con `forwardslash.htb`.
- El vhost `backup.forwardslash.htb` aloja una consola de API y un formulario XML.
- `/dev/` está restringido por IP y por usuario.

## Enumeración

- `profilepicture.php` acepta una URL y muestra el contenido; también acepta rutas locales.
- Los filtros `php://filter/convert.base64-encode/resource=...` permiten leer el código fuente.
- `config.php` del vhost backup contiene credenciales de `chiv`; el formulario `/dev/` es vulnerable a XXE.

## Foothold

Se lee el código de `profilepicture.php` y el de `/dev/`, donde aparece una contraseña de FTP/SSH para `chiv`. Con esos credenciales se entra por SSH.

```bash
curl -s 'http://backup.forwardslash.htb/profilepicture.php'   --data-urlencode 'url=php://filter/convert.base64-encode/resource=/var/www/backup.forwardslash.htb/dev/index.php'
```

La flag de usuario se obtiene tras el pivote a `pain`.

## Movimiento lateral

`chiv` puede ejecutar un programa de backup que carga una biblioteca o un archivo de configuración de forma insegura. Se abusa para leer `/home/pain/config.php` y obtener su contraseña; después se usa `su` o SSH como `pain`.

## Escalada de privilegios

`pain` tiene `encryptorinator/ciphertext` y un script Python con un cifrado por suma de bytes. Se hace fuerza bruta con `rockyou.txt` hasta que el texto descifrado sea legible y se obtiene la frase de paso del volumen LUKS. `sudo` permite `cryptsetup luksOpen` y `mount`; dentro hay una clave privada de root.

```bash
python3 brute.py
sudo /sbin/cryptsetup luksOpen /var/backups/recovery/encrypted_backup.img backup
sudo /bin/mount /dev/mapper/backup ./mnt/
cat ./mnt/id_rsa
```

## Evidencia

- Código fuente leído con `php://filter`.
- Acceso SSH como `chiv` y `pain`.
- Texto descifrado con la frase de paso y `id_rsa` de root montada.

## Lecciones aprendidas

- La inclusión de archivos debe restringirse a rutas y extensiones permitidas.
- Un cifrado casero suele ser reversible con texto conocido o fuerza bruta.
- `sudo` sobre `cryptsetup` y `mount` permite leer cualquier volumen preparado.

## Mitigación y detección

- Sustituir includes dinámicos por plantillas y validar rutas.
- Deshabilitar entidades externas y DTD en el parser XML.
- No conceder `cryptsetup`/`mount` sin control de imágenes y puntos de montaje.

## Referencias

- [0xdf — ForwardSlash](https://0xdf.gitlab.io/2020/07/04/htb-forwardslash.html)
- [IppSec — ForwardSlash](https://www.youtube.com/watch?v=alJa51XylDE)
- [Hack The Box — ForwardSlash](https://app.hackthebox.com/machines/forwardslash)
