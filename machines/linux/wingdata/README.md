---
machine: WingData
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, wingftp, cve-2025-47812, null-byte, lua, tarfile, privesc]
---

# WingData — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Wing FTP Server 7.4.3 permite acceso anónimo y es vulnerable a CVE-2025-47812: un null byte en el usuario inyecta Lua en el archivo de sesión y da RCE como `wingftp`. Los archivos de cuentas contienen hashes con sal; uno se crackea y la contraseña se reutiliza para `wacky`. `wacky` ejecuta como root un script Python de restauración de backups, y CVE-2025-4517 permite escribir fuera del directorio de extracción mediante un tar con symlinks.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con `wingdata.htb`.
- El panel es Wing FTP Server 7.4.3 y permite acceso anónimo.
- `feroxbuster` enumera `/admin`, `/login` y rutas de descarga.

## Enumeración

El servidor tiene acceso anónimo y una interfaz web. La versión 7.4.3 es anterior a 7.4.4 y vulnerable a CVE-2025-47812: un null byte en el nombre de usuario permite inyectar código Lua en el archivo de sesión que Wing FTP ejecuta.

## Foothold

Se envía un usuario con `%00` y una instrucción Lua que ejecuta una reverse shell; el servidor la interpreta al cargar la sesión y se obtiene una shell como `wingftp`.

## Movimiento lateral

Los archivos de cuentas de Wing FTP contienen hashes con sal. Se copian y se crackean con Hashcat; la contraseña de `wacky` se reutiliza en el sistema.

```bash
hashcat -m 17200 hashes.txt rockyou.txt
ssh wacky@wingdata.htb
```

## Escalada de privilegios

`wacky` puede ejecutar como root el script de restauración:

```bash
sudo /usr/local/bin/python3 /opt/backup_clients/restore_backup_clients.py <BACKUP>
```

El script usa `tarfile` con el filtro `data`, vulnerable a CVE-2025-4517. Se crea un tar con un symlink que apunta a `/root/.ssh/authorized_keys` y una ruta que escapa del directorio de extracción; la validación se salta y se escribe la clave pública de root.

## Evidencia

- Wing FTP 7.4.3 y acceso anónimo.
- CVE-2025-47812 y shell `wingftp`.
- Hashes de cuentas y `wacky`.
- Script de restauración como root.
- CVE-2025-4517 y clave de root.

## Lecciones aprendidas

- Un null byte puede truncar la validación y colar código en un archivo de sesión.
- Los hashes de aplicaciones se reutilizan en el sistema.
- `tarfile` con filtros antiguos no impide escrituras fuera del destino.
- Un script de restauración como root es un objetivo de escritura arbitraria.

## Mitigación y detección

- Actualizar Wing FTP a 7.4.4 o superior.
- Deshabilitar acceso anónimo y validar usuarios.
- Usar contraseñas únicas y hash fuerte.
- Actualizar Python y validar miembros/symlinks al extraer tar.

## Referencias

- [0xdf — WingData](https://0xdf.gitlab.io/2026/06/27/htb-wingdata.html)
- [IppSec — WingData](https://www.youtube.com/watch?v=T5VUR55e1Xg)
- [Hack The Box — WingData](https://app.hackthebox.com/machines/wingdata)
