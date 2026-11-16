---
topic: Squid y TFTP — configuración expuesta y pivote a localhost
tags: [linux, squid, tftp, proxy, pivot, credentials]
---

# Squid y TFTP — configuración expuesta y pivote a localhost

[🌐 English](squid-tftp-proxy-pivot.en.md) | **Español**

## Concepto

TFTP no ofrece listado, pero permite leer rutas conocidas como `/etc/squid/squid.conf` y `/etc/squid/passwords`. Con esas credenciales se usa Squid para alcanzar servicios que solo escuchan en localhost.

## Cuándo aplica

- TFTP en UDP 69 y Squid en 3128.
- Squid requiere autenticación básica.
- Hay servicios internos enlazados a `127.0.0.1`.

## Procedimiento

1. Descargar `squid.conf` y `passwords`.
2. Crackear el hash `$apr1$` con hashcat modo 1600.
3. Configurar el proxy y escanear `127.0.0.1`.
4. Acceder al servicio interno.

## Comandos

```bash
tftp <IP>
tftp> get /etc/squid/squid.conf
tftp> get /etc/squid/passwords
hashcat -m 1600 squid.hash rockyou.txt
curl -x http://<USER>:<PASS>@<IP>:3128 http://127.0.0.1:8080/
```

## Variantes

- Proxy para fuzzear puertos internos.
- `gobuster -p` con el proxy.
- Credenciales reutilizadas en otros servicios.

## Limitaciones

- TFTP puede estar filtrado o en solo lectura.
- Squid puede limitar destinos.
- El hash puede ser fuerte.

## Mitigación

- Deshabilitar TFTP y no guardar hashes en rutas legibles.
- Limitar Squid a destinos necesarios.
- Usar credenciales únicas y MFA.

## Detección

- Lecturas TFTP de configuración.
- Escaneos de `127.0.0.1` a través del proxy.
- Autenticación de proxy desde hosts nuevos.

## Referencias

- [0xdf — Joker](https://0xdf.gitlab.io/2020/08/13/htb-joker.html)
- [Squid — configuration](https://www.squid-cache.org/Doc/config/)
- [TFTP — RFC 1350](https://www.rfc-editor.org/rfc/rfc1350)
