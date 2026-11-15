---
title: QUIC/HTTP3 — enumerar un servicio que no habla HTTP/1.1
tags: [web, quic, http3, curl, enumeration, udp]
---

# QUIC/HTTP3 — enumerar un servicio que no habla HTTP/1.1

[🇬🇧 English](quic-http3-enumeration.en.md) | **Español**

## Concepto

QUIC transporta HTTP/3 sobre UDP y no responde a un `curl` normal. Un servicio puede parecer cerrado en TCP mientras escucha en UDP/9001 o UDP/443. Para enumerarlo hace falta un cliente con HTTP/3 y, a menudo, resolver el vhost correcto.

## Cuándo aplica

- `nmap` TCP no muestra la web, pero un escaneo UDP encuentra el puerto.
- `curl https://host:puerto` falla con error de conexión o de protocolo.
- El certificado o el banner menciona HTTP/3 o QUIC.

## Procedimiento

1. Escanear UDP y confirmar el puerto.
2. Usar un `curl` compilado con HTTP3 (`curl -V` debe incluir `HTTP3`).
3. Forzar HTTP/3 con `--http3-only`.
4. Añadir el vhost a `/etc/hosts` si el certificado lo requiere.

```bash
nmap -Pn -sU -p9001 <IP>
curl -V | grep -i http3
curl --http3-only -k https://quick.htb:9001/
```

## Variantes

- `nghttp3`/`ngtcp2` o `quiche` para pruebas de bajo nivel.
- `openssl s_client -quic` en versiones recientes.
- Si el servidor hace fallback, `--http3` puede bastar.

## Limitaciones

- Muchos `curl` de distro no incluyen HTTP3.
- Algunos firewalls bloquean UDP.
- El vhost y el SNI deben coincidir con el certificado.

## Mitigación y detección

- Inventariar servicios UDP y no asumir que solo hay TCP.
- Aplicar las mismas reglas de autenticación y WAF a HTTP/3.
- Monitorizar tráfico QUIC anómalo y escaneos UDP.
- Mantener el servidor actualizado y limitar protocolos.

## Referencias

- <https://curl.se/docs/http3.html>
- <https://www.rfc-editor.org/rfc/rfc9114.html>
- <https://blog.cloudflare.com/the-quic-approach-to-connection-migration/>
