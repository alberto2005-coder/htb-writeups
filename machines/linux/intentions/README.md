---
machine: Intentions
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, laravel, sqli, imagick, cap-dac-read-search, git]
---

# Intentions — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una galería Laravel permite registrar una cuenta y guardar preferencias. Un filtro que elimina espacios puede evadirse con comentarios SQL y provoca una inyección de segundo orden que revela hashes bcrypt. La API v2 acepta el hash como credencial, lo que da acceso de administrador. La edición de imágenes con Imagick permite RCE como `www-data`; el historial de Git filtra la contraseña de `greg`, y una capacidad `CAP_DAC_READ_SEARCH` en `/opt/scanner/scanner` se usa como oráculo MD5 para reconstruir la clave SSH de root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH y Nginx con Laravel.
- `intentions.htb`; una SPA Vue consume `/api/v1`.
- `feroxbuster` localiza `/api`, `/js` y el panel de administración.

## Enumeración

- El registro y la selección de géneros almacenan preferencias.
- El filtro elimina espacios literales, pero no `/**/`.
- La carga de la galería concatena la preferencia en una consulta.
- El bundle de administración revela `/api/v2` y el parámetro `hash`.

## Foothold

Se inyecta una consulta de segundo orden en el campo de géneros y se recupera la tabla de usuarios con hashes bcrypt. La API v2 autentica comparando el hash enviado, por lo que el hash de administrador se usa directamente. Con la sesión de admin se edita una imagen y se abusa de un pseudo-protocolo de Imagick para ejecutar comandos.

```bash
sqlmap -r request.txt --second-req feed.txt --batch
```

## Escalada de privilegios

Se revisa el historial de Git y se obtiene la contraseña de `greg`. `greg` pertenece al grupo `scanner` y puede ejecutar `/opt/scanner/scanner`, con `CAP_DAC_READ_SEARCH`. El binario calcula MD5 de archivos y permite comparar bytes; se usa como oráculo para reconstruir la clave privada SSH de root byte a byte y entrar como root.

```bash
getcap -r / 2>/dev/null
./scanner -p /root/.ssh/id_rsa
```

## Evidencia

- Respuesta de la API con hashes bcrypt.
- Acceso al panel de administración usando el hash.
- Ejecución de `id` como `www-data` desde Imagick.
- `getcap` y reconstrucción de la clave de root.

## Lecciones aprendidas

- Eliminar espacios no es una defensa contra SQLi.
- Un hash no debe ser una credencial.
- Las capacidades Linux pueden convertir un binario de solo lectura en un oráculo.

## Mitigaciones y detección

- Usar consultas parametrizadas y validar la entrada en el servidor.
- No aceptar hashes como prueba de autenticación.
- Restringir Imagick y las capacidades; auditar `CAP_DAC_READ_SEARCH`.
- Revisar el historial de Git antes de publicar un repositorio.
- Referencias: HTB Intentions, 0xdf, CWE-89, capabilities(7).

## Referencias

- <https://www.hackthebox.com/machines/Intentions>
- <https://bryanmcnulty.com/posts/htb-intentions>
- <https://cwe.mitre.org/data/definitions/89.html>
- <https://attack.mitre.org/techniques/T1190/>
