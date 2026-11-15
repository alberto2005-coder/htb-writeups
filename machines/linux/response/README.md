---
machine: Response
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, hmac, ldap, forensics, pcap]
---

# Response — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación expone un SSRF con un oráculo HMAC que permite firmar peticiones al chat interno. Se redirige la autenticación LDAP a un servidor propio para entrar como administrador, se encadena una petición cross-protocol hacia FTP y se añade un host al escáner para leer una clave SSH mediante un traversal en el estado de un certificado. Un PCAP y un core dump de Meterpreter permiten reconstruir la clave de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- Puertos: `22/tcp` SSH, `80/tcp` HTTP y `443/tcp` HTTPS.
- Servicios: Proxy web, chat interno, LDAP, FTP y un escáner de hosts.
- Tecnologías: SSRF, HMAC, LDAP, TLS, PCAP, Meterpreter y análisis de memoria.

## Enumeración

- `response.htb` con un proxy que acepta URLs.
- Chat interno accesible solo desde la red del servidor.
- Oráculo HMAC que firma parámetros.
- Escáner que procesa hosts y certificados.

## Foothold

Se construye un proxy que usa el SSRF y el oráculo HMAC para firmar y reenviar peticiones al chat. Se crea un servidor LDAP falso que responde a la autenticación como administrador; así se habla con el bot y se obtienen credenciales FTP.

```bash
python3 ssrf_hmac_proxy.py --target http://response.htb --listen 0.0.0.0:8000
python3 rogue_ldap.py --listen 0.0.0.0:389 --user admin
curl -x http://127.0.0.1:8000 http://chat.internal/
```

## Movimiento lateral

El bot entrega credenciales de FTP, pero no son accesibles directamente. Se envía un enlace que provoca una petición cross-protocol y se leen los archivos del FTP; después se registra un host propio para que el escáner lo procese.

## Escalada de privilegios

El escáner acepta un certificado cuyo estado incluye un traversal; se usa para leer la clave SSH del siguiente usuario. El PCAP y el core dump de Meterpreter contienen tráfico cifrado y la clave AES; al descifrarlo aparece un ZIP con una captura y `authorized_keys`, suficientes para reconstruir la clave privada de root.

```bash
openssl req -new -x509 -nodes -out cert.pem -keyout key.pem \
  -subj '/CN=../../../../home/<USER>/.ssh/id_rsa'
# Enviar el certificado al escáner y recoger la clave leída
tshark -r capture.pcap -Y 'tcp.port == 4444'
volatility3 -f core.dmp windows.pslist
# Descifrar el tráfico y reconstruir la clave con la captura y authorized_keys
```

## Evidencia

- Peticiones firmadas al chat y respuesta del bot.
- Archivos FTP leídos mediante la petición cross-protocol.
- Clave SSH y reconstrucción de la clave de root desde el ZIP.

## Lecciones aprendidas

- Un SSRF con firma válida puede atravesar confianzas internas.
- La autenticación LDAP sin validación de servidor permite un rogue LDAP.
- Los artefactos forenses (PCAP y core dump) pueden contener claves y secretos.

## Mitigación y detección

- Validar destinos, resolver DNS de forma segura y bloquear rangos internos.
- Firmar con contexto y caducidad; no exponer un oráculo HMAC.
- Usar LDAPS con validación estricta y rotar claves tras una intrusión.

## Referencias

- [0xdf — Response](https://0xdf.gitlab.io/2023/02/04/htb-response.html)
- [IppSec — Response](https://www.youtube.com/watch?v=-t1UAvTxB94)
- [Hack The Box — Response](https://app.hackthebox.com/machines/response)
