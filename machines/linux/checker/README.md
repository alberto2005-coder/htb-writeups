---
machine: Checker
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, teampass, bookstack, race-condition, privesc]
---

# Checker — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Teampass 3.0.0.22 es vulnerable a CVE-2023-1545: un SQLi en la búsqueda vuelca hashes, uno se crackea y da acceso a BookStack y a SSH. SSH pide 2FA, pero BookStack CVE-2023-6199 permite SSRF y un oráculo de filtros PHP para leer el `.google_authenticator` desde un backup. Para root, `check_leak` usa memoria compartida y un race condition permite inyectar el comando que ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,8080 <IP>
```

- `22` SSH, `80` BookStack y `8080` Teampass.
- `ffuf` con `Host: FUZZ.checker.htb` confirma `checker.htb` y `books.checker.htb`.
- Teampass muestra su versión y el login.

## Enumeración

- La búsqueda de Teampass es vulnerable a CVE-2023-1545.
- El SQLi vuelca `login`, `pw` y `token` de `teampass_users`.
- Los hashes son bcrypt; uno se crackea con diccionario.

## Foothold

Con la contraseña crackeada se entra a Teampass y se lee una entrada con credenciales de `reader` para SSH y BookStack. SSH pide un código TOTP, pero BookStack permite leer `/backup/home_backup/home/reader/.google_authenticator`.

```bash
bash cve-2023-1545.sh http://<IP>:8080
hashcat -m 3200 hashes.txt rockyou.txt
```

## Movimiento lateral

BookStack 23.10.2 es vulnerable a CVE-2023-6199. Se usa el SSRF con `php://filter` y un oráculo de errores para reconstruir el archivo de 2FA; después se genera el código y se entra por SSH.

```bash
ssh reader@checker.htb
```

## Escalada de privilegios

`check_leak` es un binario de root que crea una clave de memoria compartida predecible, lee una cadena y la pasa a una consulta. Un proceso en bucle escribe un comando en esa memoria durante la ventana de carrera; la siguiente ejecución lo corre como root.

```bash
while true; do ./poison; done
sudo /usr/local/bin/check_leak
```

## Evidencia

- Versión de Teampass y SQLi CVE-2023-1545.
- Hash crackeado y credenciales de `reader`.
- `php://filter` sobre el backup y código TOTP.
- Memoria compartida envenenada y shell root.

## Lecciones aprendidas

- Un gestor de contraseñas comprometido entrega credenciales de varios sistemas.
- Un SSRF con oráculo de errores puede leer archivos aunque no haya eco directo.
- Una clave de `shm` predecible y un `sleep` convierten un binario root en una carrera explotable.

## Mitigación y detección

- Actualizar Teampass y BookStack; parametrizar las consultas.
- No guardar backups de homes en rutas accesibles por la aplicación.
- Usar `shmget` con IPC_PRIVATE y no ejecutar comandos desde memoria compartida.

## Referencias

- [0xdf — Checker](https://0xdf.gitlab.io/2025/05/31/htb-checker.html)
- [IppSec — Checker](https://www.youtube.com/watch?v=mywIX1F1Cr8)
- [Hack The Box — Checker](https://app.hackthebox.com/machines/checker)
