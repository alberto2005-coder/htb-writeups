---
machine: Gofer
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, smb, ssrf, gopher, phishing, suid, privesc]
---

# Gofer — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un share SMB anónimo contiene un correo con pistas: un proxy en desarrollo y una usuaria propensa al phishing. `proxy.gofer.htb` solo bloquea GET, pero acepta POST con `url`, y permite SSRF por gopher. Se envía un correo interno con un ODT malicioso, se obtiene `jhudson`, y `tcpdump` captura la autenticación básica de `tbuckley`. El SUID `notes` tiene un use-after-free que permite ponerse rol admin y ejecutar `tar` sin ruta absoluta, lo que da root por PATH hijacking.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,25,80,445 <IP>
```

- `22` SSH, `25` SMTP/Postfix, `80` Apache y `445` Samba.
- `smbclient -N //<IP>/shares` permite leer un share anónimo.
- `ffuf` con `Host: FUZZ.gofer.htb` descubre `proxy.gofer.htb`.

## Enumeración

- El share contiene `.backup/mail`, un correo interno que menciona phishing, ODT y un proxy sin restringir.
- El proxy responde 401 a GET, pero POST/OPTIONS a `/index.php` devuelven 200.
- `index.php?url=` acepta gopher, no bloquea `gofer.htb` y permite inyectar saltos de línea con doble URL-encode.

## Foothold

Se usa gopher para hablar con SMTP en localhost y enviar un correo a `jhudson` con un enlace a un ODT que ejecuta una macro al abrirlo. La usuaria lo descarga y se obtiene una shell como `jhudson`.

```text
gopher://127.0.0.1:25/_HELO%20x%250d%250aMAIL%20FROM...
```

## Movimiento lateral

`jhudson` está en `netdev` y `tcpdump` tiene capabilities, así que puede capturar tráfico local. Se filtran peticiones HTTP y aparece la cabecera `Authorization: Basic` del proxy; se decodifica y la contraseña de `tbuckley` funciona por SSH.

```bash
tcpdump -i any -nn -A 'tcp port 80 and (tcp[((tcp[12:1] & 0xF0) >> 2):4] = 0x47455420)'
```

## Escalada de privilegios

`notes` es SUID/SGID de root y solo lo puede ejecutar el grupo `dev`, al que pertenece `tbuckley`. Tras crear y borrar un usuario, el puntero liberado se reutiliza como buffer de la nota; 24 bytes de relleno permiten escribir `admin` en el rol. La opción 8 ejecuta `tar -czvf ...` sin ruta absoluta; se coloca un `tar` malicioso en `.` y se antepone al `PATH`.

```bash
export PATH=.:$PATH
printf '#!/bin/bash\nbash -i\n' > tar && chmod +x tar
notes
```

## Evidencia

- Correo del share y proxy con SSRF gopher.
- ODT con macro y shell como `jhudson`.
- `tcpdump` capturando la cabecera Basic de `tbuckley`.
- Use-after-free en `notes`, rol admin y `tar` secuestrado.

## Lecciones aprendidas

- Los shares SMB olvidados filtran contexto y nombres de usuarios.
- Restringir solo GET no protege un proxy.
- Un SUID con lógica de roles en memoria y `system` sin ruta es una escalada directa.

## Mitigación y detección

- Cerrar shares anónimos y revisar correos internos.
- Validar método y esquema en el proxy; bloquear gopher y destinos internos.
- Corregir el use-after-free y usar rutas absolutas en binarios privilegiados.

## Referencias

- [0xdf — Gofer](https://0xdf.gitlab.io/2023/10/28/htb-gofer.html)
- [IppSec — Gofer](https://www.youtube.com/watch?v=waKs935HxNE)
- [Hack The Box — Gofer](https://app.hackthebox.com/machines/gofer)
