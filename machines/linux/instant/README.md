---
machine: Instant
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, android, apk, jwt, swagger, directory-traversal, solarputty, privesc]
---

# Instant — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Se descompila el APK Android y se encuentran los subdominios `mywalletv1.instant.htb` y `swagger-ui.instant.htb`, además de un JWT de administrador embebido. Con ese token se accede a la API y a su documentación; un endpoint permite directory traversal y lectura de archivos, con el que se obtiene la clave SSH de `shirohige`. En `/opt/backups/Solar-PuTTY/` hay un `sessions-backup.dat` de SolarPuTTY; el descifrado recupera la contraseña de root y `su` cierra la máquina.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH 9.6p1 Ubuntu.
- `80`: Apache httpd 2.4.58.

```bash
echo '<IP> instant.htb mywalletv1.instant.htb swagger-ui.instant.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://instant.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

La web principal distribuye una aplicación Android (`instant.apk`). Se descomprime y se analiza con `jadx-gui`; del código salen:

- La URL de la API `mywalletv1.instant.htb`.
- La documentación Swagger en `swagger-ui.instant.htb`.
- Un JWT de administrador escrito en el código.
- El flujo de login y los endpoints de la cartera.

```bash
unzip instant.apk -d apk
jadx-gui instant.apk
```

## Foothold

El JWT embebido se usa como `Authorization: Bearer` contra la API. Swagger documenta un endpoint que recibe un nombre de archivo; el parámetro permite `../` y se convierte en una lectura arbitraria. Se leen `/etc/passwd`, el `user.txt` y la clave privada SSH de `shirohige`.

```bash
curl -s 'http://mywalletv1.instant.htb/api/v1/admin/read/log?log=../../../home/shirohige/.ssh/id_rsa' \
  -H 'Authorization: Bearer <JWT>'
```

La clave se reconstruye y se entra por SSH como `shirohige`.

## Movimiento lateral

No hay otro host. En el home hay `logs/` y `projects/`, con el código de la API. La enumeración se centra en archivos de configuración y credenciales guardadas por herramientas de escritorio.

## Escalada de privilegios

En `/opt/backups/Solar-PuTTY/` aparece `sessions-backup.dat`, un archivo de sesiones de SolarPuTTY. SolarPuTTY cifra las credenciales con una contraseña maestra; las herramientas públicas `SolarPuttyDecrypt` (C#) y `SolarPuttyCracker` (Python) permiten descifrarlas. La contraseña recuperada es la de root, y `su` da la shell.

```bash
python3 SolarPuttyCracker.py sessions-backup.dat -w /usr/share/wordlists/rockyou.txt
su root
```

## Evidencia

- APK descompilado con subdominios y JWT embebido.
- Petición a Swagger con el token de administrador.
- Directory traversal y lectura de `/etc/passwd` y de la clave SSH.
- Sesión SSH como `shirohige`.
- `sessions-backup.dat` descifrado y contraseña de root.
- `id` con UID 0.

## Lecciones aprendidas

- Un APK es código y puede contener secretos y endpoints internos.
- Los JWT embebidos en clientes no son secretos.
- Un parámetro de nombre de archivo sin normalizar permite traversal.
- Las herramientas de gestión de sesiones guardan credenciales que se pueden descifrar.
- La reutilización de contraseñas entre el escritorio y root es un riesgo directo.

## Mitigaciones y detección

- No incluir secretos ni tokens de administrador en aplicaciones móviles.
- Validar y normalizar rutas; usar un identificador en lugar de un nombre de archivo.
- Aplicar autorización por objeto y por usuario en la API.
- Cifrar las sesiones con contraseñas robustas y no reutilizar la de root.
- Rotar credenciales y revisar archivos de sesión en los homes.
- Alertar de peticiones con `../`, de uso de JWT de larga duración y de `su` a root.

## Referencias

- [0xdf — Instant](https://0xdf.gitlab.io/2025/03/01/htb-instant.html)
- [IppSec — Instant](https://www.youtube.com/watch?v=Oyh84PHjzsQ)
- [Hack The Box — Instant](https://app.hackthebox.com/machines/instant)
- [Knowledge — Recuperación de credenciales de SolarPuTTY](../../../knowledge/linux/solarputty-credential-recovery.md)
