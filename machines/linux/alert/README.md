---
machine: Alert
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, xss, markdown, file-read, cron, php]
---

# Alert — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un visor de Markdown permite inyectar HTML y JavaScript; el bot administrador visita el enlace y ejecuta una XSS que lee páginas internas. Un directory traversal en `messages.php` obtiene el `.htpasswd` de `statistics.alert.htb`, cuyo hash se crackea para entrar por SSH como `albert`. Un cron de root ejecuta un PHP del monitor web con un archivo de configuración escribible, lo que permite crear una bash SUID.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<DOMAIN> -H "Host: FUZZ.<DOMAIN>"
```

## Enumeración

- La web convierte Markdown a HTML y conserva el HTML embebido.
- `statistics.alert.htb` pide autenticación básica.
- El formulario de contacto envía una URL al bot administrador.

## Acceso inicial

Se publica un Markdown con un `<script>` que hace `fetch` a `messages.php?file=../../../../var/www/statistics.alert.htb/.htpasswd` y envía el resultado a un servidor propio. El bot lo ejecuta y se obtiene el hash de `albert`, que se crackea y se reutiliza por SSH.

## Escalada de privilegios

`/opt/website-monitor` se ejecuta como root desde cron. Uno de los archivos que incluye es escribible por `albert`; se añade una línea que copia bash a `/tmp`, le pone propietario root y el bit SUID, y se ejecuta para leer la flag.

## Evidencia

- Petición del bot con el contenido de `.htpasswd`.
- Hash crackeado y acceso SSH como `albert`.
- Archivo de configuración modificado y bash SUID ejecutada.

## Lecciones aprendidas

- El Markdown que permite HTML sin sanitizar amplía la superficie XSS.
- Los paneles internos suelen confiar en archivos de contraseñas accesibles por traversal.
- Un cron de root sobre código editable es una escalada directa.

## Mitigación y detección

- Sanitizar el HTML generado y aplicar CSP.
- Servir los archivos de autenticación fuera del document root.
- Montar el monitor con permisos de solo lectura y usuario sin privilegios.

## Referencias

- [0xdf — Alert](https://0xdf.gitlab.io/2025/03/22/htb-alert.html)
- [IppSec — Alert](https://www.youtube.com/watch?v=zSBEfW46zd0)
- [Hack The Box — Alert](https://app.hackthebox.com/machines/alert)
