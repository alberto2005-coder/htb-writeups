---
challenge: Illumination
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, git, historial, base64, secretos]
---

# Illumination — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

El ZIP trae `bot.js`, `config.json` y el directorio **`.git`** completo. El `config.json` actual tiene el token sustituido por un texto de relleno, pero en el **historial** hay un commit anterior con el token real en base64. `git log` / `git show` lo recuperan y `base64 -d` da la flag.

## Enunciado y superficie

"Un desarrollador junior acaba de cambiarse a una nueva plataforma de control de código fuente. ¿Puedes encontrar el token secreto?" El artefacto es el repositorio entero, no un volcado de ficheros.

## Reconocimiento

```bash
unzip Illumination.zip && cd Illumination.JS
ls -la
git log --oneline --all
git log -p --all -- config.json
```

Estructura: `bot.js`, `config.json`, `.git/`. El `config.json` actual:

```json
{"token": "Replace me with token when in use! Security Risk!",
 "prefix": "~", "lightNum": "1337",
 "username": "UmVkIEhlcnJpbmcsIHJlYWQgdGhlIEpTIGNhcmVmdWxseQ==",
 "host": "127.0.0.1"}
```

## Explicación del fallo

`bot.js` hace `client.login(Buffer.from(config.token, 'base64').toString('ascii'))`: el token se guarda en base64 y se decodifica en tiempo de ejecución. El `username` en base64 dice literalmente *"Red Herring, read the JS carefully"* — es una distracción deliberada.

El historial tiene cuatro commits: el inicial crea el token real, y uno posterior lo sustituye con el mensaje *"I removed the unique token as it was a security risk"*. Borrar un secreto en un commit **no** lo elimina del repositorio.

## Explotación

```bash
git show 47241a4:config.json        # o el commit donde se elimina
# "-       "token": "SFRCe3YzcnNpMG5fYzBudHIwbF9hbV9JX3JpZ2h0P30=","
echo 'SFRCe3YzcnNpMG5fYzBudHIwbF9hbV9JX3JpZ2h0P30=' | base64 -d
```

```text
HTB{...}
```

Si `git log` pareciera vacío, `git fsck --lost-found` rescata commits huérfanos.

## Evidencia

```text
.
├── bot.js
├── config.json
└── .git/
```

Salidas recortadas; la flag no se publica.

## Lecciones aprendidas

- **Mirar sólo el fichero actual**: el token ya no está ahí; sin `.git` no hay reto.
- **El `username`** es una pista falsa a propósito; no lleva a la flag.
- **El commit que "limpia"** es el que señala dónde estaba el secreto.

- Un `.git` publicado es una copia de seguridad de **todos** los secretos que alguna vez se commitearon.
- Rotar el token no basta si el historial sigue accesible.
- Mitigación: `.git` fuera del artefacto, escaneo de secretos en CI y reescritura del historial más rotación de credenciales.
