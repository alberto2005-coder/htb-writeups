---
topic: Request smuggling h2c
tags: [web, http2, h2c, smuggling, proxy]
---

# Request smuggling h2c

[🌐 English](http2-request-smuggling.en.md) | **Español**

## Concepto

Un proxy acepta HTTP/2 en claro (h2c) y reenvía la petición al backend sin normalizar el protocolo. El atacante introduce una petición HTTP/1.1 dentro del flujo h2c para alcanzar rutas que el frontend bloquea.

## Cuándo aplica

- Frontend que aplica reglas por ruta y backend que acepta h2c.
- Cadenas proxy/caché con conversión de protocolo.
- Cabeceras `Upgrade: h2c` o `HTTP2-Settings` aceptadas sin validación.

## Procedimiento

1. Comprobar si el servidor acepta h2c con `curl --http2-prior-knowledge`.
2. Enviar una petición a una ruta bloqueada y comparar el código.
3. Construir el smuggling con `h2cSmuggler` o una petición cruda.
4. Verificar que el backend procesa la ruta interna.

```bash
curl --http2-prior-knowledge -sv http://<HOST>/admin
python3 h2cSmuggler.py -u http://<HOST>/admin
# Petición cruda con Upgrade: h2c y HTTP2-Settings
```

## Variantes

- Conversión HTTP/2 a HTTP/1.1 en el proxy.
- Smuggling CL.TE/TE.CL combinado con h2c.
- Rutas internas protegidas solo por el frontend.
- Caché envenenada con la respuesta interna.

## Limitaciones

- El backend debe aceptar h2c o el proxy debe reenviarlo.
- Las reglas del proxy pueden normalizar las cabeceras.
- La ruta interna debe existir y ser sensible.

## Mitigación y detección

- Rechazar h2c en el borde y usar HTTP/2 solo con TLS.
- Normalizar el protocolo y las cabeceras en cada salto.
- Aplicar autorización en el backend, no solo en el proxy.

## Referencias

- <https://portswigger.net/web-security/request-smuggling>
- <https://www.rfc-editor.org/rfc/rfc9113>
- <https://attack.mitre.org/techniques/T1190/>
