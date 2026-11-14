---
machine: OneTwoSeven
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, sftp, symlink, plugin-upload, apt, mitm]
---

# OneTwoSeven — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un proveedor de hosting da acceso SFTP sin shell. Los symlinks permiten leer el panel de administración y obtener credenciales; un bypass en la subida de plugins instala una webshell como `www-admin-data`. La regla sudo permite `apt-get update/upgrade` y conserva `http_proxy`; se monta un repositorio falso y se envenena el paquete `telnet` para ejecutar código como root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,60080 <IP>
ssh -p 22 <USER>@<IP>
```

## Enumeración

- El puerto 22 solo ofrece SFTP; el 60080 está filtrado desde fuera.
- El panel muestra un usuario por defecto y un gestor de plugins.
- `/etc/apt/sources.list.d/onetwoseven.list` apunta a un repositorio propio.

## Acceso inicial

Se crean symlinks en el directorio SFTP hacia archivos del panel y se leen a través de la web. Con las credenciales de `ots-admin` se entra al panel del 60080 y se reenvía el puerto por SSH. La subida de plugins deshabilita el botón, pero añadir el parámetro esperado directamente en la petición permite subir un ZIP con PHP y ejecutarlo como `www-admin-data`.

## Escalada de privilegios

`sudo -l` permite `apt-get update` y `apt-get upgrade`, y `env_keep` conserva `http_proxy`. Se configura un proxy propio, se responde por `packages.onetwoseven.htb` con un `Release`/`Packages` falso y se publica un `telnet` con `postinst` malicioso. `apt-get upgrade` lo instala como root y ejecuta el script.

## Evidencia

- Symlinks visibles desde el listado web.
- Acceso al panel y webshell como `www-admin-data`.
- Peticiones de apt al proxy y ejecución del `postinst`.

## Lecciones aprendidas

- Los symlinks de un servicio de archivos pueden cruzar hacia el document root.
- Deshabilitar un botón no elimina el endpoint.
- Un proxy de apt controlado por el usuario rompe la cadena de confianza.

## Mitigación y detección

- Chroot o jaula para SFTP y prohibir symlinks fuera del home.
- Validar el paquete y el MIME en el servidor, no solo en la interfaz.
- No conservar proxies en sudo y firmar los repositorios.

## Referencias

- [0xdf — OneTwoSeven](https://0xdf.gitlab.io/2019/08/31/htb-onetwoseven.html)
- [IppSec — OneTwoSeven](https://www.youtube.com/watch?v=EXuEDHFjS9E)
- [Hack The Box — OneTwoSeven](https://app.hackthebox.com/machines/onetwoseven)
