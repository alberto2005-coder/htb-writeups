---
machine: Forgot
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, host-header, cache-poisoning, pickle, privesc]
---

# Forgot — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El formulario de recuperación genera el enlace con la cabecera `Host`, así que se envía a la víctima un enlace hacia el atacante y se roba el token de `robert`. Después, un fallo de caché en Varnish sirve la sesión del administrador y expone un ticket con credenciales de `diego`. `diego` puede ejecutar un script de seguridad como root que carga modelos `.sav` con `pickle`, lo que permite ejecutar código.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 20.04 y `80/tcp` con una web Flask.
- El vhost `forgot.htb` tiene login, registro y recuperación de contraseña.
- Varnish cachea respuestas de `/static` y el servidor usa Werkzeug.

## Enumeración

- El usuario `robert-dev-<número>` es válido y el reset se genera dinámicamente.
- Cambiar `Host` por la IP del atacante hace que el enlace de reset apunte allí.
- La caché de Varnish puede almacenar una página autenticada si se fuerza el `Host` y la ruta adecuada.

## Foothold

Se solicita el reset para `robert-dev-<número>` con `Host: <ATTACKER>` y se captura el token. Se cambia la contraseña, se entra como Robert y se envía un enlace de reset al administrador. La respuesta autenticada del admin queda en caché y se recupera; contiene un ticket con credenciales de `diego`.

```bash
python3 -m http.server 80
# POST /forgot con Host: <ATTACKER>
# GET /reset?token=... en el servidor atacante
ssh diego@forgot.htb
```

## Movimiento lateral

`diego` tiene acceso SSH y puede enumerar los scripts locales. El ticket y la caché ya han dado el salto desde la web; el siguiente paso es el script privilegiado.

## Escalada de privilegios

`sudo -l` permite `/opt/security/ml_security.py`. El script carga modelos `.sav` con `pickle.load` desde `/opt/security/lib`. Se reemplaza uno de esos modelos por un pickle malicioso y, al ejecutarse como root, el payload crea una shell SUID o ejecuta un comando.

```bash
sudo -l
ls -l /opt/security/lib
# reemplazar un .sav por un pickle con __reduce__ malicioso
sudo /opt/security/ml_security.py
```

## Evidencia

- Token de reset capturado con `Host` malicioso.
- Sesión de admin cacheada y ticket con credenciales de `diego`.
- Modelo `.sav` reemplazado y ejecución como root.

## Lecciones aprendidas

- Los enlaces de reset no deben construirse con la cabecera `Host`.
- La caché puede mezclar respuestas autenticadas entre usuarios.
- `pickle` sobre modelos o datos externos es ejecución de código.

## Mitigación y detección

- Fijar el dominio del reset en la configuración y validar `Host`.
- No cachear respuestas autenticadas; usar `Cache-Control: private`.
- Firmar o validar modelos y evitar `pickle` con archivos modificables.

## Referencias

- [0xdf — Forgot](https://0xdf.gitlab.io/2023/03/04/htb-forgot.html)
- [IppSec — Forgot](https://www.youtube.com/watch?v=wKcTELVst20)
- [Hack The Box — Forgot](https://app.hackthebox.com/machines/forgot)
