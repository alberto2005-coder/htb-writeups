---
challenge: Illumination
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, git, base64, secretos-en-historial]
type: Forensics
---


# Illumination — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

El ZIP contiene `bot.js`, `config.json` y un directorio **`.git`**. El `config.json` actual tiene el token puesto a “Replace me”, pero en el **historial de git** hay una versión anterior con el token real, en base64. Se recupera con `git log` / `git show` y se decodifica.

## Enunciado y superficie

- Categoría Forensics; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

El ZIP contiene `bot.js`, `config.json` y un directorio **`.git`**. El `config.json` actual tiene el token puesto a “Replace me”, pero en el **historial de git** hay una versión anterior con el token real, en base64. Se recupera con `git log` / `git show` y se decodifica.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

```text
.
├── bot.js
├── config.json
└── .git/
```

```json
{"token": "Replace me with token when in use! Security Risk!",
 "prefix": "~", "lightNum": "1337",
 "username": "UmVkIEhlcnJpbmcsIHJlYWQgdGhlIEpTIGNhcmVmdWxseQ==", "host": "127.0.0.1"}
```

El `username` es una distracción evidente (dice literalmente «red herring, lee el JS con cuidado»).

## Lecciones aprendidas

- **Mirar sólo el fichero actual**: el token ya no está ahí; sin `.git` no hay reto.
- **`username`**: es una pista falsa a propósito; no lleva a la flag.
- **Objetos sueltos**: si `git log` parece vacío, `git fsck --lost-found` rescata commits huérfanos.

- Un `.git` publicado es un backup completo del código y de **todos** los secretos que alguna vez se commitearon.
- Borrar un secreto en un commit posterior no lo elimina: hay que reescribir el historial y rotarlo.
- Un token filtrado se considera comprometido aunque el servicio ya no lo use.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)

## Método

1. **Ver el historial** del repositorio:

```bash
git log --oneline --all
git log -p --all -- config.json
```

2. **Recuperar la versión filtrada**: al principio de la historia el token estaba en claro en el JSON; el commit posterior lo sustituye por el texto de relleno. Con `git show <commit>:config.json` se obtiene el valor original.

3. **Decodificar**: el token comprometido viene en base64.

```bash
echo '<token>' | base64 -d
```

4. **Comprobarlo** con el propio bot (el prefijo `~` delata el comando que usa el token).
