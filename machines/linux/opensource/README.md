---
machine: OpenSource
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, flask, path-join, docker, gitea, git-hooks]
---

# OpenSource — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web permite descargar `source.zip` y subir archivos. `os.path.join` descarta las rutas anteriores cuando el nombre es absoluto, así que se escribe fuera de `uploads`. Se sobrescribe una vista de Flask y se ejecuta código como root en el contenedor. Desde ahí se accede a Gitea en el host, se recupera la clave SSH de `dev01` y un hook de Git ejecutado por un cron root da una shell SUID.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 18.04, `80/tcp` Flask y `3000/tcp` Gitea.
- La web tiene `/download` para el código fuente y `/upcloud` para subir archivos.
- El código descargado incluye `.git`, `Dockerfile` y la configuración de supervisord.

## Enumeración

- `source.zip` revela que la aplicación corre como root en un contenedor.
- `get_file_name` elimina `../`, pero no una barra inicial.
- `os.path.join(cwd, "public", "uploads", "/app/app/views.py")` devuelve `/app/app/views.py`.

## Foothold

Se sube un archivo llamado `/app/app/views.py` con una vista que ejecuta una reverse shell, y se visita la ruta para dispararla.

```bash
# En Burp, cambiar filename a /app/app/views.py
curl http://<IP>/0xdf
nc -lnvp 443
```

## Movimiento lateral

El contenedor alcanza Gitea en `172.17.0.1:3000`. Se usa `chisel` para exponerlo y se entra con las credenciales de `dev01`; el repositorio `home-backup` contiene su clave SSH privada. Con la clave se accede a `dev01` en el host.

## Escalada de privilegios

Un cron root ejecuta `/usr/local/bin/git-sync` en el home de `dev01`, que hace `git commit` y `git push`. Se escribe un hook `pre-commit` que copia `/bin/bash` y le da SUID; el cron lo ejecuta como root.

```bash
echo -e '#!/bin/bash
cp /bin/bash /tmp/rootbash
chown root:root /tmp/rootbash
chmod 4777 /tmp/rootbash' > ~/.git/hooks/pre-commit
chmod +x ~/.git/hooks/pre-commit
/tmp/rootbash -p
```

## Evidencia

- `source.zip` y ruta absoluta en la subida.
- Shell root en el contenedor y Gitea expuesto con chisel.
- Clave de `dev01` y hook `pre-commit` ejecutado por cron.

## Lecciones aprendidas

- `os.path.join` con una ruta absoluta ignora los componentes anteriores.
- Un contenedor root con el código montado permite modificar la aplicación.
- Los hooks de Git se ejecutan en operaciones automatizadas y pueden ser abusados.

## Mitigación y detección

- Normalizar y confinar las rutas de subida; rechazar nombres absolutos.
- Ejecutar contenedores sin root y con el código de solo lectura.
- Revisar hooks y crons que ejecuten Git como root.

## Referencias

- [0xdf — OpenSource](https://0xdf.gitlab.io/2022/10/08/htb-opensource.html)
- [IppSec — OpenSource](https://www.youtube.com/watch?v=z6nJNr8AFTU)
- [Hack The Box — OpenSource](https://app.hackthebox.com/machines/opensource)
