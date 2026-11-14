---
machine: Zipping
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, zip, symlink, sqli, webshell, reverse-engineering]
---

# Zipping — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación permite subir un ZIP y lo descomprime con una ruta controlable. Un enlace simbólico dentro del archivo permite leer archivos fuera del directorio de subida y obtener el código fuente. La auditoría revela una SQLi que escribe un webshell y una LFI para ejecutarlo; un binario con `sudo` se resuelve con ingeniería inversa.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH y Apache.
- La web permite subir un ZIP de un proyecto.
- Hay una sección de descarga y una ruta de administración.

## Enumeración

- El formulario valida la extensión, pero no el contenido del ZIP.
- Un enlace simbólico a `/var/www/html` se conserva al extraer.
- La descarga devuelve archivos del servidor y revela el código.
- El código contiene una consulta SQL construida con entrada del usuario.

## Foothold

Se crea un ZIP con un symlink y se sube. Al descargar el resultado se obtiene el código fuente y la configuración. Con la SQLi se escribe un PHP en una ruta servida; la LFI carga el archivo y ejecuta comandos.

```bash
ln -s /var/www/html target
zip --symlinks payload.zip target
```

## Escalada de privilegios

Un binario disponible con `sudo` pide una contraseña y contiene la lógica de comparación. Se analiza con `strings`, `ltrace` y un desensamblador; la contraseña se usa para ejecutar el binario como root.

```bash
sudo -l
strings /path/to/binary
ltrace ./binary
```

## Evidencia

- ZIP con symlink aceptado.
- Código fuente descargado.
- Consulta SQLi y webshell ejecutado.
- Binario analizado y root.

## Lecciones aprendidas

- Validar la extensión no valida el contenido de un archivo.
- Los symlinks dentro de archivos comprimidos pueden escapar del destino.
- Una SQLi con escritura de archivos suele terminar en RCE.
- La ingeniería inversa básica resuelve binarios con `sudo`.

## Mitigaciones y detección

- Extraer con opciones que rechacen symlinks y rutas absolutas.
- Usar consultas parametrizadas y permisos mínimos de escritura.
- Revisar binarios con `sudo` y no incrustar secretos en la comparación.
- Alertar de ZIPs con enlaces y escrituras en el document root.
- Referencias: OWASP File Upload, CWE-59, HTB Zipping.

## Referencias

- <https://www.hackthebox.com/machines/Zipping>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://cwe.mitre.org/data/definitions/59.html>
- <https://attack.mitre.org/techniques/T1505/003/>
