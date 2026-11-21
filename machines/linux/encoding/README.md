---
machine: Encoding
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, file-read, git, ssrf, php-filter, git-hooks, systemd, privesc]
---

# Encoding — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio principal tiene una lectura de archivos que permite descargar el repositorio `.git` de un vhost que no es accesible directamente. Del código salen el vhost `api.haxtables.htb` y una inclusión local de archivos; un SSRF llega a esa inclusión y una cadena de filtros PHP (`php://filter`) convierte la lectura en RCE como `www-data`. `www-data` puede ejecutar como `svc` el script `git-commit.sh`; el directorio `.git` es escribible, así que se instala un hook `post-commit` que añade una clave SSH a `svc`. `svc` puede reiniciar servicios con `systemctl` como root y `/etc/systemd/system` es escribible mediante ACL: se modifica una unidad para ejecutar una shell y se reinicia.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH 8.9p1 Ubuntu.
- `80`: Apache httpd 2.4.52.

```bash
echo '<IP> haxtables.htb image.haxtables.htb api.haxtables.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://haxtables.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

El sitio principal es una página de herramientas. El vhost `image.haxtables.htb` ofrece una utilidad que recibe una URL o un nombre de archivo y devuelve contenido. Al probar rutas relativas se confirma una lectura de archivos; con ella se descarga el repositorio `.git` de `api.haxtables.htb`, que no responde directamente desde fuera.

El repositorio contiene el código de la API: rutas, parámetros y una llamada que incluye archivos. También aparece el script `git-commit.sh` y la configuración del servicio.

## Foothold

La API expone una inclusión local en un parámetro de plantilla. El SSRF desde el sitio de imágenes permite alcanzar esa ruta desde localhost, y la inclusión se convierte en ejecución encadenando filtros PHP:

```text
php://filter/convert.iconv.../resource=<PAYLOAD>
```

El resultado es una webshell o una reverse shell como `www-data`.

## Movimiento lateral

`www-data` puede ejecutar el script de commit como otro usuario:

```text
(svc) NOPASSWD: /var/www/image/scripts/git-commit.sh
```

El directorio `/var/www/image/.git` tiene una ACL que da escritura a `www-data`. Se crea `.git/hooks/post-commit` con una clave pública SSH y se provoca un commit con `git-commit.sh`; el hook se ejecuta como `svc` y añade la clave a su `authorized_keys`. El contenido del hook es:

```bash
#!/bin/bash
mkdir -p /home/svc/.ssh
echo '<PUBLIC_KEY>' >> /home/svc/.ssh/authorized_keys
chmod 600 /home/svc/.ssh/authorized_keys
```

## Escalada de privilegios

`svc` puede reiniciar cualquier servicio como root:

```text
(root) NOPASSWD: /usr/bin/systemctl restart *
```

`/etc/systemd/system` es escribible por `svc` mediante ACL. Se copia o modifica una unidad para que `ExecStart` ejecute una shell o copie `bash` con setuid, se recarga el daemon y se reinicia el servicio. El proceso resultante corre como root.

```bash
systemctl daemon-reload
sudo systemctl restart <SERVICE>
```

## Evidencia

- Lectura de archivos en `image.haxtables.htb` y descarga del `.git` de la API.
- SSRF hacia la inclusión local y ejecución de `id` como `www-data`.
- ACL escribible en `.git` y hook `post-commit` ejecutado como `svc`.
- `sudo -l` con `systemctl restart *`.
- ACL escribible en `/etc/systemd/system` y unidad modificada.
- `id` con UID 0 tras reiniciar el servicio.

## Lecciones aprendidas

- Una lectura de archivos puede exponer un repositorio Git completo aunque el vhost no sea accesible.
- Los filtros PHP permiten convertir un LFI en RCE sin subir un archivo.
- Un SSRF puede alcanzar servicios que solo escuchan en localhost.
- Los hooks de Git se ejecutan con el usuario que hace el commit.
- `sudo systemctl restart *` sobre unidades escribibles es root directo.

## Mitigaciones y detección

- No permitir rutas arbitrarias en utilidades de imágenes o descargas; usar listas de permitidos.
- Bloquear `php://filter` y validar esquemas y rutas en inclusiones.
- Restringir SSRF con listas de destinos y sin acceso a localhost.
- Proteger `.git` y sus hooks; no dar escritura al usuario web.
- Evitar `sudo systemctl restart *`; permitir solo unidades concretas y no escribibles.
- Alertar de commits automáticos, hooks nuevos y reinicios de servicios fuera de ventana.

## Referencias

- [0xdf — Encoding](https://0xdf.gitlab.io/2023/04/15/htb-encoding.html)
- [IppSec — Encoding](https://www.youtube.com/watch?v=iyGvnmkx1es)
- [Hack The Box — Encoding](https://app.hackthebox.com/machines/encoding)
- [Knowledge — Escalada con hooks de Git](../../../knowledge/linux/git-hooks-privesc.md)
