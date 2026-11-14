---
topic: Memcached — enumeración sin autenticación
tags: [linux, memcached, enumeration, cache, credentials]
---

# Memcached — enumeración sin autenticación

[🌐 English](memcached-enumeration.en.md) | **Español**

## Concepto

Memcached escucha por defecto en 11211 sin autenticación. Si está expuesto, `stats`, `stats items` y `lru_crawler metadump all` permiten listar claves y recuperar sesiones, tokens o credenciales cacheadas.

## Cuándo aplica

- Puerto 11211 accesible directamente o por SSRF/proxy.
- Aplicaciones que cachean sesiones o consultas.
- Instancias antiguas sin SASL ni firewall.

## Procedimiento

1. Confirmar el servicio con `nc` y `stats`.
2. Listar slabs y claves con `stats items`.
3. Volcar claves con `lru_crawler metadump all`.
4. Inspeccionar valores en busca de sesiones o credenciales.
5. Reutilizar los datos en la aplicación.

## Comandos

```bash
printf 'stats\r\n' | nc -nv <HOST> 11211
printf 'stats items\r\n' | nc -nv <HOST> 11211
printf 'lru_crawler metadump all\r\n' | nc -nv <HOST> 11211
```

## Variantes

- UDP/11211 para amplificación o enumeración.
- Claves de sesión de PHP o Rails.
- Credenciales de base de datos cacheadas.

## Limitaciones

- El servicio puede requerir SASL.
- Las claves pueden haber expirado.
- El firewall puede limitar el origen.

## Mitigación

- Escuchar solo en `127.0.0.1`.
- Filtrar 11211 y usar SASL.
- No cachear secretos en claro.

## Detección

- Conexiones externas a 11211 y comandos `stats`/`metadump`.
- Picos de tráfico de caché desde hosts no habituales.

## Referencias

- <https://memcached.org/>
- <https://attack.mitre.org/techniques/T1552/>
