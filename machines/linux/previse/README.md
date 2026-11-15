---
machine: Previse
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, execute-after-redirect, command-injection, hashcat, path-hijack, privesc]
---

# Previse — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un execute-after-redirect permite acceder a `accounts.php` sin sesión y crear un usuario. El código fuente descargado revela una inyección de comandos en `logs.php`, que da `www-data`. La base filtra hashes y uno se crackea para `m4lwhere`; `/opt/scripts/access_backup.sh` se ejecuta como root y llama a `gzip` sin ruta absoluta, lo que permite un path hijack.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con `previse.htb`.
- La web tiene login, registro y un menú de gestión.
- `gobuster` encuentra `accounts.php`, `logs.php`, `download.php` y `status.php`.

## Enumeración

`accounts.php` responde con un 302 si no hay sesión, pero el código sigue ejecutándose después de enviar la redirección. Se intercepta la respuesta y se cambia el 302 por un 200 para ver el formulario; se crea un usuario y se inicia sesión.

## Foothold

Con sesión se descarga el código fuente desde `download.php`. `logs.php` pasa `delim` sin sanear a `exec()`:

```php
$output = exec("/usr/bin/python /opt/scripts/log_process.py {$_POST['delim']}");
```

Se inyecta `; bash -c '...'` y se obtiene `www-data`.

## Movimiento lateral

`config.php` contiene las credenciales de MySQL. Se dumpean los hashes de `accounts` y se crackea el de `m4lwhere`; la contraseña se reutiliza en el sistema.

```bash
hashcat -m 500 hashes.txt rockyou.txt
ssh m4lwhere@previse.htb
```

## Escalada de privilegios

`m4lwhere` puede ejecutar `/opt/scripts/access_backup.sh` como root. El script llama a `gzip` sin ruta absoluta y el directorio `/dev/shm` es escribible. Se coloca un `gzip` malicioso, se antepone `/dev/shm` al `PATH` y se ejecuta el script.

```bash
export PATH=/dev/shm:$PATH
sudo /opt/scripts/access_backup.sh
```

## Evidencia

- EAR en `accounts.php`.
- Inyección en `logs.php` y `www-data`.
- Hashes de MySQL y `m4lwhere`.
- `access_backup.sh`, `gzip` y root.

## Lecciones aprendidas

- Un `header("Location")` sin `exit` no detiene la ejecución.
- `exec()` con entrada del usuario es inyección directa.
- Los hashes de la base se reutilizan en el sistema.
- Un script root con binarios sin ruta absoluta es path hijack.

## Mitigación y detección

- Terminar la ejecución después de una redirección.
- Usar `escapeshellarg` y listas blancas.
- Hashes únicos y contraseñas separadas.
- Usar rutas absolutas y un `PATH` seguro en scripts root.

## Referencias

- [0xdf — Previse](https://0xdf.gitlab.io/2022/01/08/htb-previse.html)
- [IppSec — Previse](https://www.youtube.com/watch?v=LI9mw1rMKVw)
- [Hack The Box — Previse](https://app.hackthebox.com/machines/previse)
