---
machine: Extension
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, laravel, hash-length-extension, docker, gitea, password-reset]
---

# Extension — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Tres vhosts (snippets, RoundCube y Gitea) filtran usuarios y hashes; una contraseña compartida da acceso y un IDOR revela el repositorio de Gitea. El reseteo de contraseña solo cambia los últimos caracteres, así que se acumulan cientos de tokens y se toma la cuenta de `charlie`. En el código, un SHA-256(secreto+email) protege una inyección de comandos; un ataque de extensión de hash la salta y da una shell en el contenedor, desde donde `docker.sock` permite leer la clave SSH de root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<IP> -H "Host: FUZZ.<DOMAIN>"
```

## Enumeración

- `snippet.htb`, `mail.snippet.htb` y `dev.snippet.htb` ejecutan la app, RoundCube y Gitea.
- La API de usuarios devuelve hashes; uno compartido se crackea como contraseña débil.
- El reset genera tokens que solo varían en los últimos dígitos y no invalidan los anteriores.

## Acceso inicial

Tras entrar con la contraseña compartida, un IDOR muestra un snippet con credenciales de Gitea y el nombre de `jean`. Se automatizan cientos de solicitudes de reset para `charlie` y se prueban los tokens; al ser válidos varios, se cambia la contraseña del administrador y se accede a Gitea.

## Escalada de privilegios

El repositorio contiene `AdminController::validateEmail`, que ejecuta `ping` con el dominio del email si el checksum SHA-256(secreto+email) coincide. Con un checksum conocido y una longitud de secreto de 40, `hash_extender` añade `@$(...)` y conserva la firma. La shell resultante es `application` dentro de un contenedor con `docker.sock`; se crea un contenedor privilegiado con `/` montado y se lee la clave privada de root del host.

## Evidencia

- Hashes y usuarios devueltos por la API.
- Reset de `charlie` con un token acumulado.
- Inyección validada por hash extension y contenedor con `/host`.

## Lecciones aprendidas

- Los tokens de reset deben ser aleatorios, de un solo uso e invalidar los previos.
- Un checksum con secreto no sustituye un MAC seguro.
- Un `docker.sock` accesible equivale a root en el host.

## Mitigación y detección

- Invalidar tokens antiguos y comparar con tiempo constante.
- Usar HMAC y no concatenar secretos con entrada del usuario.
- No montar el socket de Docker en contenedores de aplicación.

## Referencias

- [0xdf — Extension](https://0xdf.gitlab.io/2023/03/18/htb-extension.html)
- [IppSec — Extension](https://www.youtube.com/watch?v=qNsbf3EmLrA)
- [Hack The Box — Extension](https://app.hackthebox.com/machines/extension)
