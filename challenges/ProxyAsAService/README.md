---
challenge: ProxyAsAService
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, ssrf, localhost-bypass, http]
---

# ProxyAsAService — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un proxy web permite solicitar URLs y bloquea `localhost`/`127.0.0.1` con una lista negra. Variantes de representación de la IP y redirecciones permiten alcanzar el servicio interno y leer la flag.

## Enunciado y superficie

- Web, Medium, retirado.
- Formulario que recibe una URL.
- Filtro que bloquea destinos locales.

```bash
curl 'http://<HOST>/?url=http://example.com'
```

## Reconocimiento

Se confirma que el backend hace la petición. Se prueban destinos internos y se observa el mensaje de bloqueo.

```bash
curl 'http://<HOST>/?url=http://127.0.0.1:80'
```

## Análisis

1. Se prueban representaciones alternativas: `127.1`, `0.0.0.0`, `[::1]`, decimal, octal.
2. Se usa un dominio propio que redirige a `localhost`.
3. Se accede al puerto interno.
4. Se lee la ruta de la flag.
5. Se documenta el bypass.

```bash
curl 'http://<HOST>/?url=http://127.1:<PORT>/'
curl 'http://<HOST>/?url=http://<ATTACKER>/redirect'
```

## Explicación del fallo

La defensa se basa en una lista negra de cadenas, no en resolver y validar la IP final. Las redirecciones y formatos alternativos evitan el filtro.

## Reproducción local

1. Montar un proxy con lista negra.
2. Exponer un servicio interno.
3. Probar variantes.
4. Añadir allowlist/validación de IP.
5. Comparar.

## Evidencia

- Petición bloqueada.
- Bypass y respuesta interna.
- Flag redactada.

## Lecciones aprendidas

- Las listas negras de `localhost` son evadibles.
- Resolver DNS antes de conectar es clave.
- Las redirecciones pueden saltar el filtro.
- SSRF afecta a servicios internos.

## Mitigación y detección

- Allowlist de destinos.
- Resolver y validar la IP final.
- Bloquear rangos privados y metadata.
- No seguir redirecciones automáticamente.

## Referencias

- <https://www.hackthebox.com/challenges/proxyasaservice>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://github.com/swisskyrepo/PayloadsAllTheThings>
