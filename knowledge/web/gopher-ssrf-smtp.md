---
topic: SSRF con gopher — correo interno por SMTP
tags: [web, ssrf, gopher, smtp, phishing]
---

# SSRF con gopher — correo interno por SMTP

[🇬🇧 English](gopher-ssrf-smtp.en.md) | **Español**

## Concepto

Un proxy que solo bloquea `GET` puede aceptar `POST` con el parámetro `url`. Si permite el esquema `gopher`, cada byte de la URL se convierte en una conexión TCP; con `%0d%0a` se habla SMTP, Redis, HTTP interno o cualquier protocolo de texto. Así se envía correo desde `localhost` sin autenticación y se evade la exposición externa.

## Cuándo aplica

- Un proxy o webhook valida el método pero no el esquema.
- El servicio interno confía en conexiones desde `127.0.0.1`.
- SMTP escucha en localhost y acepta correo sin autenticación.

## Procedimiento

1. Confirmar que `POST` llega al backend y que `url` es controlable.
2. Probar `gopher://127.0.0.1:25/` y observar la respuesta.
3. Construir la secuencia SMTP con CRLF doblemente codificados.
4. Enviar un correo con un enlace o adjunto malicioso.

```text
gopher://127.0.0.1:25/_HELO%20localhost%250d%250aMAIL%20FROM%3A%3Cattacker%40local%3E%250d%250aRCPT%20TO%3A%3Cvictim%40local%3E%250d%250aDATA%250d%250aSubject%3A%20test%250d%250a%250d%250ahello%250d%250a.%250d%250aQUIT%250d%250a
```

## Variantes

- `gopher://` contra Redis para escribir un archivo o un módulo.
- `dict://` para servicios de texto simples.
- Redirección 302 a `gopher://` si el proxy solo valida la URL inicial.

## Limitaciones

- El esquema gopher debe estar permitido.
- El proxy puede normalizar o bloquear CRLF.
- El servidor SMTP puede requerir TLS o autenticación.

## Mitigación

- Allowlist de esquemas y destinos; bloquear IPs privadas y loopback.
- Resolver y validar la IP después de cada redirección.
- Requerir autenticación en SMTP y limitar el relay local.

## Detección

- Peticiones del proxy a `127.0.0.1`, `[::1]` o rangos privados.
- Conexiones SMTP sin autenticación desde el servidor web.
- URLs con `%250d%250a` o `gopher://` en logs.

## Referencias

- [0xdf — Gofer](https://0xdf.gitlab.io/2023/10/28/htb-gofer.html)
- [curl — gopher protocol](https://curl.se/docs/manpage.html#gopher)
- [CWE-918 — Server-Side Request Forgery](https://cwe.mitre.org/data/definitions/918.html)
