---
machine: Analytics
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, metabase, cve-2023-38646, docker, overlayfs]
---

# Analytics — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Metabase 0.46.6 en `data.analytical.htb` es vulnerable a CVE-2023-38646 (RCE preautenticación). El shell cae en un contenedor Docker; las variables de entorno filtran credenciales SSH del host. En el host, el kernel 6.2.0-25 es vulnerable a GameOverlay (CVE-2023-2640 + CVE-2023-32629) y permite root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

El puerto 80 redirige a `analytical.htb`. Se añade al hosts y se enumeran vhosts:

```bash
ffuf -u http://analytical.htb -H 'Host: FUZZ.analytical.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

Aparece `data.analytical.htb`, con una instancia de Metabase.

## Acceso inicial

Se identifica la versión en `/app/dist/app-main.js` o en el HTML. Metabase 0.46.6 es vulnerable a CVE-2023-38646:

```bash
curl -s http://data.analytical.htb/api/session/properties | jq .'setup-token'
```

Con el token de setup se envía un payload a `/api/setup/validate`. El campo `details.db` admite un `connection_uri` con driver H2 y `INIT=RUNSCRIPT FROM ...`, lo que ejecuta comandos dentro del contenedor. Se usa un servidor HTTP local para entregar el script y un listener para la reverse shell.

```bash
python3 -m http.server 8000
nc -lvnp 4444
```

## Del contenedor al host

```bash
id
hostname
env
```

El contenedor expone variables de entorno con credenciales de la base de datos y del usuario del host. Se reutilizan por SSH:

```bash
ssh <USER>@<IP>
```

## Escalada a root

```bash
uname -a
# 6.2.0-25-generic
```

La versión es vulnerable a GameOverlay. Se compila o descarga un exploit de CVE-2023-2640/CVE-2023-32629 y se ejecuta en un namespace de usuario:

```bash
unshare -rm sh -c 'mkdir -p l u w m && ...'
```

El binario con `setuid(0)` devuelve una shell root. Se lee la flag y se redacta.

## Evidencia

- Respuesta de `api/session/properties` con el token de setup redactado.
- Petición a `api/setup/validate` y shell en el contenedor.
- `uname -a`, `env` y ejecución del exploit overlayfs.

## Lecciones aprendidas

- Un vhost olvidado puede exponer una instancia vulnerable.
- El token de setup de Metabase es sensible incluso antes del login.
- Las variables de entorno de un contenedor suelen contener credenciales del host.
- GameOverlay afecta a kernels Ubuntu con el parche de OverlayFS incompleto.

## Mitigación y detección

- Actualizar Metabase y restringir `/api/setup`.
- No ejecutar contenedores con credenciales del host en variables de entorno.
- Aplicar parches de kernel y limitar namespaces de usuario.
- Detectar peticiones a `api/setup/validate` con `connection_uri` y procesos H2 inusuales.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2023-38646>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-2640>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-32629>
- <https://www.hackthebox.com/machines/analytics>
