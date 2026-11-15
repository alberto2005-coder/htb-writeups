---
machine: Cybermonday
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nginx, laravel, jwt, redis, docker, privesc]
---

# Cybermonday — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un off-by-slash de nginx filtra `.env` y el repositorio; un mass assignment da admin y acceso a una API de webhooks con JWT. La confusión de algoritmos permite firmar como admin, y un webhook con CRLF interactúa con Redis para envenenar la sesión de Laravel y ejecutar código. Desde el contenedor se enumera un registro Docker, se extrae la imagen de la API y se filtra la contraseña de `john`; un script de `docker compose` mal validado permite montar el host.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nginx con `cybermonday.htb`.
- La web es una tienda Laravel; `feroxbuster` encuentra `/api` y rutas de administración.
- Un off-by-slash en la configuración de nginx permite leer `.env` y el `.git`.

## Enumeración

- El perfil actualiza todos los campos y permite `isAdmin=true` (mass assignment).
- Como admin aparece `webhooks-api-beta.cybermonday.htb`.
- La API usa JWT RS256 y publica su clave pública en JWKS.

## Foothold

La verificación acepta el algoritmo del token. Se cambia a HS256 y se firma con la clave pública como secreto (algorithm confusion), obteniendo un token de admin. Con él se crea un webhook `sendRequest` que hace SSRF.

Un CRLF en la URL del webhook permite hablar con Redis y modificar la sesión de Laravel. Se usa `phpggc` para generar un objeto y se obtiene ejecución como `www-data` dentro del contenedor.

## Movimiento lateral

En la red interna hay un registro Docker. Con credenciales débiles se lista `bolt-image`/la imagen de la API, se descarga y se revisa el código. Un endpoint adicional con cabecera especial permite leer archivos y filtrar la contraseña de `john`, que funciona por SSH.

## Escalada de privilegios

`john` puede ejecutar `/opt/secure_compose.py` como root con cualquier `.yml`. El script valida el compose, pero se puede saltar la comprobación y lanzar un contenedor con el filesystem del host montado o con `apparmor:unconfined`. Dentro del contenedor se lee `/root/root.txt` o se escribe una clave.

```bash
sudo /opt/secure_compose.py /tmp/docker-compose.yml
```

## Evidencia

- Off-by-slash y `.env`.
- Mass assignment y API de webhooks.
- JWT algorithm confusion.
- SSRF/CRLF contra Redis y RCE en Laravel.
- Registro Docker y contraseña de `john`.
- `secure_compose.py` y root.

## Lecciones aprendidas

- Un off-by-slash de nginx expone archivos fuera del root.
- El mass assignment puede conceder roles administrativos.
- Aceptar el algoritmo del JWT rompe la validación asimétrica.
- CRLF en una URL puede convertir SSRF en acceso a Redis.
- Validar un compose no es suficiente si se permite montar el host.

## Mitigación y detección

- Corregir el alias de nginx y bloquear `.env`/`.git`.
- Listas blancas de campos y roles.
- Fijar el algoritmo JWT y validar `kid`/issuer.
- Aislar Redis y validar URLs de webhooks.
- Ejecutar compose sin privilegios y con volúmenes restringidos.

## Referencias

- [0xdf — Cybermonday](https://0xdf.gitlab.io/2023/12/02/htb-cybermonday.html)
- [IppSec — Cybermonday](https://www.youtube.com/watch?v=VNMn5bXA8XY)
- [Hack The Box — Cybermonday](https://app.hackthebox.com/machines/cybermonday)
