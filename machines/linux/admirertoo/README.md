---
machine: AdmirerToo
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, adminer, ssrf, opentsdb, fail2ban, opencats]
---

# AdmirerToo — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Galería con Adminer 4.7.8 y un OpenTSDB interno. Un SSRF en Adminer (CVE-2021-21311) alcanza OpenTSDB y su inyección de comandos (CVE-2020-35476) da shell como `opentsdb`; las credenciales de `servers.php` permiten SSH como `jennifer`. En localhost, OpenCats 0.9.5.2 (CVE-2021-25294) escribe `whois.conf` y fail2ban ejecuta la consulta `whois`, logrando root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<DOMAIN> -H "Host: FUZZ.<DOMAIN>"
```

## Enumeración

- `db.admirer-gallery.htb` expone Adminer 4.7.8 con una sesión ya iniciada.
- Los puertos 4242 (OpenTSDB) y 8080 (OpenCats) solo escuchan en localhost.
- `servers.php` de Adminer guarda credenciales de la base y de `jennifer`.

## Acceso inicial

Se usa el módulo de login de Elasticsearch para que Adminer haga una petición a un servidor propio que responde con un `301` hacia `http://127.0.0.1:4242`. El SSRF llega a OpenTSDB y se explota su inyección de comandos para obtener una shell como `opentsdb`. La lectura de `servers.php` revela la contraseña de `jennifer`, reutilizada en SSH.

## Escalada de privilegios

Como `jennifer` se descubre OpenCats en el 8080. La deserialización PHP de CVE-2021-25294 permite escribir un archivo; se genera una cadena con `phpggc` para crear `/usr/local/etc/whois.conf`. fail2ban ejecuta `whois` sobre la IP atacante y el archivo manipula la consulta para inyectar un comando como root.

## Evidencia

- Respuesta de Adminer con el contenido de OpenTSDB.
- Shell como `opentsdb` y posterior acceso SSH como `jennifer`.
- `whois.conf` modificado y ejecución de fail2ban como root.

## Lecciones aprendidas

- Un SSRF con redirects puede alcanzar servicios ligados a loopback.
- Los paneles de administración filtran credenciales de otros servicios.
- fail2ban ejecuta binarios del sistema con configuración influenciable por el atacante.

## Mitigación y detección

- Restringir Adminer y exigir autenticación fuerte.
- No ejecutar OpenTSDB sin autenticación en localhost.
- Controlar la escritura en `/usr/local/etc` y revisar las acciones de fail2ban.

## Referencias

- [0xdf — AdmirerToo](https://0xdf.gitlab.io/2022/05/28/htb-admirertoo.html)
- [IppSec — AdmirerToo](https://www.youtube.com/watch?v=446sWtb5bc4)
- [Hack The Box — AdmirerToo](https://app.hackthebox.com/machines/admirertoo)
