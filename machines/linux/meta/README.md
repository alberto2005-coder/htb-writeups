---
machine: Meta
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, exiftool, cve-2021-22204, command-injection, cron, pspy]
---

# Meta — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un vhost acepta imágenes y usa ExifTool para procesar metadatos. La versión es vulnerable a CVE-2021-22204 y permite ejecución de comandos al procesar un DjVu malicioso. La enumeración de tareas revela un cron editable que lleva a root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

Se enumeran vhosts con `ffuf`/`wfuzz`; se añade el subdominio de gestión al hosts. La aplicación permite subir imágenes y muestra los metadatos.

## Acceso inicial

Se identifica ExifTool en una versión vulnerable. Se crea una imagen DjVu con un payload en los metadatos:

```bash
exiftool -config exploit.config image.jpg
```

Al subirla y procesarla, el comando se ejecuta. Se obtiene una shell como el usuario del servicio.

## Movimiento lateral

```bash
pspy64
```

Se observa un cron que ejecuta un script propiedad del usuario. Se modifica el script para lanzar una reverse shell como el usuario que ejecuta la tarea.

## Escalada a root

Se repite la enumeración de procesos y tareas. Se localiza otro script o binario ejecutado por root con permisos de escritura, o una regla `sudo` mal configurada. Se inyecta un comando y se obtiene root.

## Evidencia

- Versión de ExifTool y archivo DjVu.
- Petición de subida y shell.
- Salida de `pspy`.
- Script modificado y shell root.

## Lecciones aprendidas

- Los metadatos de imágenes son una superficie de ataque.
- ExifTool antiguo permite ejecución al parsear DjVu.
- `pspy` descubre tareas sin acceso a `crontab`.
- Los scripts de cron con permisos débiles son escalada.

## Mitigación y detección

- Actualizar ExifTool y validar imágenes.
- Ejecutar el procesamiento en un sandbox sin red.
- Restringir escritura en scripts de cron.
- Monitorizar procesos hijos de `exiftool` y cron.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2021-22204>
- <https://www.hackthebox.com/machines/meta>
- <https://github.com/DominicBreuker/pspy>
