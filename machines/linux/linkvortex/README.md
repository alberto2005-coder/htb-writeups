---
machine: LinkVortex
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, ghost-cms, cve-2023-40028, git-dumper, symlink, toctou]
---

# LinkVortex — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un `.git` expuesto permite recuperar credenciales de Ghost. La versión es vulnerable a CVE-2023-40028, una lectura arbitraria mediante enlaces simbólicos. La configuración filtrada da acceso SSH y un script `sudo` con una carrera TOCTOU permite root.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,80 <IP>
```

- SSH y HTTP.
- Vhosts `linkvortex.htb` y `dev.linkvortex.htb`.

## Enumeración

- La raíz web contiene un directorio `.git` accesible.
- `git-dumper` recupera el repositorio y su historial.

```bash
git-dumper http://linkvortex.htb/.git repo/
git log --all --oneline
```

- En el historial aparecen credenciales de un usuario de Ghost.

## Foothold

Ghost 5.x es vulnerable a CVE-2023-40028: un usuario autenticado puede subir un enlace simbólico y leer archivos arbitrarios a través de la descarga.

```bash
# Autenticarse en /ghost y preparar la subida del symlink
curl -s -b cookies.txt "http://linkvortex.htb/ghost/api/admin/files/upload/"
```

Se lee `config.production.json` o la configuración equivalente para obtener la contraseña del usuario del sistema.

## Movimiento lateral

La contraseña de Ghost se reutiliza para SSH.

```bash
ssh bob@linkvortex.htb
```

## Escalada de privilegios

`sudo -l` muestra un script de limpieza que comprueba un archivo y después opera sobre él. Entre la comprobación y el uso se puede sustituir el archivo por un enlace simbólico.

```bash
sudo -l
ln -sf /etc/sudoers.d/<FILE> /ruta/comprobada
sudo /usr/local/bin/<CLEANUP_SCRIPT>
```

La carrera TOCTOU permite escribir o modificar un archivo privilegiado y obtener root.

## Evidencia

- `.git` expuesto y commits recuperados.
- Petición de subida del symlink.
- Archivo de configuración leído, con secretos redactados.
- `sudo -l` y ejecución del script.
- Flag redactada.

## Lecciones aprendidas

- `.git` expuesto filtra mucho más que código.
- Los enlaces simbólicos rompen validaciones basadas solo en rutas.
- Una comprobación y un uso separados abren una ventana TOCTOU.

## Mitigaciones y detección

- Bloquear `.git` y cualquier archivo de control de versiones.
- Actualizar Ghost a una versión corregida.
- Resolver rutas y rechazar symlinks en scripts privilegiados.
- Auditar `sudo` sobre scripts que manipulan archivos temporales.

## Referencias

- <https://www.hackthebox.com/machines/linkvortex>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-40028>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://attack.mitre.org/techniques/T1548/001/>
