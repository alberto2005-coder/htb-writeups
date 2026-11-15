---
machine: CrimeStoppers
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, lfi, php-filter, zip-wrapper, apache-module, privesc]
---

# CrimeStoppers — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un LFI en `?op=` permite leer el código con `php://filter` y subir un ZIP que se incluye con `zip://`, lo que da RCE como `www-data`. El perfil de Thunderbird de `dom` contiene su contraseña y permite pasar a ese usuario. Un módulo Apache modificado (`rootme`) ejecuta comandos como root al recibir una petición concreta.

## Reconocimiento

```bash
nmap -Pn -sCV -p80 <IP>
```

- Solo `80` Apache 2.4.25 en Ubuntu 17.04.
- La web es una galería de FSociety con `/uploads` y `/upload.php`.
- `gobuster` encuentra `index.php?op=`, `upload.php` y `uploads/`.

## Enumeración

El parámetro `op` se concatena con `.php`. `php://filter` devuelve el código fuente en base64.

```bash
curl -s 'http://<IP>/?op=php://filter/convert.base64-encode/resource=home' | base64 -d
```

El código muestra que la subida guarda archivos en `uploads/<IP>/` con un nombre aleatorio y que `op` se incluye sin validar.

## Foothold

Se sube un ZIP con un `shell.php`; el wrapper `zip://` lo incluye y ejecuta.

```text
?op=zip://uploads/<IP>/<FILE>.zip#shell.php&cmd=id
```

La shell corre como `www-data`.

## Movimiento lateral

En `/home/dom` hay un perfil de Mozilla/Thunderbird. `mozilla2john.py` extrae el hash del `key3.db`; la contraseña maestra está vacía. Al abrir el perfil se recupera la contraseña de `dom`, que funciona con `su`.

```bash
python3 mozilla2john.py key3.db > key3.hash
john key3.hash
su dom
```

## Escalada de privilegios

El módulo `apache_modrootme` está cargado en Apache y modificado para ejecutar comandos como root. El correo de `dom` documenta el backdoor y la petición que lo activa; al enviarla se obtiene una shell de root.

```bash
apachectl -M | grep rootme
```

## Evidencia

- LFI con `php://filter` y código fuente.
- ZIP subido e incluido con `zip://`.
- Perfil de Thunderbird y contraseña de `dom`.
- Módulo Apache `rootme` y root.

## Lecciones aprendidas

- `php://filter` convierte un LFI en divulgación de código.
- Los wrappers `zip://` y `phar://` amplían un LFI a ejecución.
- Los perfiles de correo guardan credenciales del sistema.
- Un módulo Apache malicioso es persistencia y root.

## Mitigación y detección

- Nunca incluir rutas controladas por el usuario; usar listas blancas.
- Deshabilitar wrappers innecesarios y validar las subidas.
- Proteger los perfiles de correo y no reutilizar contraseñas.
- Verificar módulos Apache y comparar con los paquetes oficiales.

## Referencias

- [0xdf — CrimeStoppers](https://0xdf.gitlab.io/2018/06/03/htb-crimestoppers.html)
- [IppSec — CrimeStoppers](https://www.youtube.com/watch?v=bgKth1K44QA)
- [Hack The Box — CrimeStoppers](https://app.hackthebox.com/machines/crimestoppers)
