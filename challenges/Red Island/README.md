---
challenge: Red Island
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, ssrf, gopher, redis, rce]
---

# Red Island — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un SSRF permite alcanzar Redis interno mediante `gopher://`. Se escriben claves/cron o un módulo para ejecutar comandos y leer la flag.

## Enunciado y superficie

- Web, Medium, retirado.
- Parámetro que acepta una URL.
- Redis interno sin autenticación.

```bash
curl 'http://<HOST>/?url=http://example.com'
```

## Reconocimiento

Se confirma SSRF con un listener. Se escanean puertos internos y se identifica Redis (6379).

```bash
curl 'http://<HOST>/?url=http://127.0.0.1:6379'
```

## Análisis

1. Se construye un payload `gopher://` con comandos RESP.
2. Se usa `redis-cli` o un script para generar el stream.
3. Se escribe un cron o un módulo malicioso.
4. Se ejecuta el comando.
5. Se lee la flag.

```bash
python3 gopherus.py --exploit redis
```

## Explicación del fallo

El SSRF permite protocolos arbitrarios y Redis no tiene autenticación. `gopher` transporta comandos RESP y convierte el SSRF en RCE.

## Reproducción local

1. Montar Redis y un proxy SSRF.
2. Confirmar acceso.
3. Enviar `PING` por gopher.
4. Escribir un cron.
5. Verificar la ejecución.

## Evidencia

- SSRF confirmado.
- Respuesta de Redis.
- Comando ejecutado y flag redactada.

## Lecciones aprendidas

- `gopher` amplía SSRF a protocolos TCP.
- Redis sin auth es RCE.
- Los cron del sistema son un objetivo.
- El filtrado de esquemas es esencial.

## Mitigación y detección

- Allowlist de esquemas y destinos.
- Autenticación y bind local en Redis.
- Bloquear `gopher`/`dict`/`file`.
- Monitorizar comandos Redis y cron.

## Referencias

- <https://www.hackthebox.com/challenges/red-island>
- <https://github.com/tarunkant/Gopherus>
- <https://redis.io/docs/management/security/>
