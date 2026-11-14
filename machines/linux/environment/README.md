---
machine: Environment
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, laravel, cve-2024-52301, filemanager, gpg, bash-env]
---

# Environment — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un Laravel en modo debug permite cambiar el entorno con CVE-2024-52301 y entrar en el panel interno como `preprod`. El filemanager vulnerable acepta una webshell y da `www-data`; un backup GPG y la clave privada de `hish` permiten `su`, y `sudo systeminfo` conserva `BASH_ENV`, que se usa para ejecutar una shell como root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -u http://<DOMAIN>/FUZZ
```

## Enumeración

- La portada es un Laravel con `APP_DEBUG=true`.
- La aplicación tiene un panel de acceso y un filemanager para imágenes de perfil.
- El servidor usa SQLite y expone `/home/hish` con permisos laxos.

## Acceso inicial

CVE-2024-52301 permite fijar el entorno mediante parámetros especialmente construidos; con `preprod` se omite el login del panel. En el perfil, el filemanager no valida bien la extensión y acepta un PHP que se ejecuta como `www-data`.

## Escalada de privilegios

Se leen la base SQLite y el backup `keyvault.gpg`; las claves GPG de `hish` son accesibles, así que se copian a un home temporal y se descifra el backup para obtener su contraseña. `sudo -l` muestra `systeminfo` con `env_keep=BASH_ENV`; se apunta a un script que lanza bash y se ejecuta como root.

## Evidencia

- Respuesta con el entorno `preprod` y acceso al dashboard.
- Webshell en el filemanager y `id` como `www-data`.
- Backup descifrado y shell de root mediante `BASH_ENV`.

## Lecciones aprendidas

- Debug y variables de entorno pueden alterar el flujo de autenticación.
- Los backups y las claves privadas deben tener permisos estrictos.
- `env_keep` puede convertir un sudo aparentemente inocuo en root.

## Mitigación y detección

- Desactivar debug y fijar el entorno en la configuración del servidor.
- Validar extensiones y servir uploads fuera del document root.
- No conservar `BASH_ENV` ni `ENV` en reglas sudo.

## Referencias

- [0xdf — Environment](https://0xdf.gitlab.io/2025/09/06/htb-environment.html)
- [IppSec — Environment](https://www.youtube.com/watch?v=XUEr-CM3Y6Q)
- [Hack The Box — Environment](https://app.hackthebox.com/machines/environment)
