---
topic: SSRF — curl con múltiples URLs y file://
tags: [web, ssrf, curl, file-scheme, filter-bypass]
---

# SSRF — curl con múltiples URLs y file://

[🌐 English](curl-file-scheme-ssrf.en.md) | **Español**

## Concepto

Un SSRF que llama a `curl` puede aceptar más de una URL en el mismo argumento. Aunque se bloquee `file://` en la primera, una segunda URL con ese esquema puede leer archivos locales y revelar código o secretos.

## Cuándo aplica

- La entrada se pasa directamente a `curl`.
- El filtro solo inspecciona la primera URL o busca cadenas.
- El servidor permite esquemas locales.

## Procedimiento

1. Confirmar que se puede elegir la URL.
2. Enviar dos URLs separadas por espacio.
3. Usar `file:///etc/passwd` o el código fuente.
4. Leer la respuesta y escalar.

## Comandos

```bash
url=http://<ATTACKER>/&url=file:///var/www/html/index.php
# o: url=http://<ATTACKER>/ file:///etc/passwd
```

## Variantes

- `file://` con codificación o mayúsculas.
- `gopher://` para interactuar con servicios.
- Redirecciones a esquemas locales.

## Limitaciones

- `curl` moderno puede limitar protocolos.
- El filtro puede validar cada URL.
- El proceso puede usar `--proto -file`.

## Mitigación

- Validar URL y esquema con lista blanca.
- Usar `--proto =http,https` y resolver una vez.
- No permitir que el usuario controle argumentos.

## Detección

- Peticiones con `file://`, `gopher://` o varias URLs.
- Lecturas de archivos locales desde el servicio web.
- Conexiones a destinos internos.

## Referencias

- [0xdf — Down](https://0xdf.gitlab.io/2025/06/17/htb-down.html)
- [curl — URL syntax](https://curl.se/docs/url-syntax.html)
- [PortSwigger — SSRF](https://portswigger.net/web-security/ssrf)
