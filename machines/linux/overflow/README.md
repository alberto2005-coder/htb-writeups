---
machine: Overflow
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, padding-oracle, sqli, exiftool, cve-2021-22204, toctou]
---

# Overflow — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un padding oracle en la cookie permite entrar al panel. Una SQLi lleva al CMS y una imagen manipulada explota ExifTool CVE-2021-22204 para RCE. La escalada combina un desbordamiento y un TOCTOU en un binario SUID.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
padbuster http://overflow.htb/login "SESSION=<COOKIE>" 16 -cookies "SESSION=<COOKIE>"
# SQLi
sqlmap -u "http://overflow.htb/records.php?id=1" --batch --dump
# ExifTool CVE-2021-22204
exiftool -config exploit.config image.jpg
# TOCTOU
pspy64 -pf -i 1000
while true; do ln -sf /tmp/payload /tmp/target; done
```

## Enumeración

- Cookie CBC con padding oracle y panel de administración.
- SQLi en los registros y un CMS con subida de imágenes.
- Binario SUID con comprobación de propietario y apertura posterior.

## Acceso inicial

El padding oracle forja una cookie de administrador. La SQLi en los registros revela credenciales del CMS; en la subida, una imagen DjVu con metadatos maliciosos ejecuta código mediante ExifTool.

## Escalada de privilegios

Un binario SUID comprueba el propietario de un archivo y luego lo abre, con una ventana TOCTOU. Se intercambia el archivo entre la comprobación y el uso para ejecutar código como root; el desbordamiento ayuda a controlar el flujo.

## Evidencia

- Cookie forjada y acceso al panel.
- Imagen con metadatos DjVu y callback de ExifTool.
- Archivo intercambiado durante la ventana TOCTOU y shell de root.

## Lecciones aprendidas

- ExifTool procesa metadatos de formatos exóticos y puede ejecutar código.
- Un padding oracle puede ser la puerta de un panel.
- TOCTOU convierte una comprobación en una ilusión.

## Mitigación y detección

- Actualizar ExifTool y deshabilitar formatos no necesarios.
- Firmar cookies y no filtrar errores de padding.
- Usar `openat`/`O_NOFOLLOW` y comprobar el descriptor, no la ruta.

## Referencias

- [0xdf — Overflow](https://0xdf.gitlab.io/2022/04/09/htb-overflow.html)
- [NVD — CVE-2021-22204](https://nvd.nist.gov/vuln/detail/CVE-2021-22204)
- [Hack The Box — Overflow](https://app.hackthebox.com/machines/overflow)
