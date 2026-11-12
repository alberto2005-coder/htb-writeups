---
topic: SSRF
tags: [web, ssrf, metadata, internal-services]
---

# SSRF

[🇬🇧 English](ssrf.en.md) | **Español**

## Concepto

Server-Side Request Forgery ocurre cuando el servidor realiza una petición a una URL controlada por el usuario. Permite alcanzar servicios internos, metadata cloud o saltar controles de red.

## Cuándo aplica

- Parámetros que reciben URLs, imágenes, webhooks o feeds.
- Funciones de "importar desde URL" o previsualización.
- Red interna con servicios sin autenticación.

## Requisitos

1. Un parámetro que el backend use para hacer la petición.
2. Un listener propio para confirmar el comportamiento.
3. Conocimiento de la red interna.

## Procedimiento

```bash
python3 -m http.server 8000
curl 'http://<HOST>/?url=http://<ATTACKER>:8000'
```

Se prueban destinos internos:

```text
http://127.0.0.1:<PORT>/
http://localhost:<PORT>/
http://169.254.169.254/latest/meta-data/
```

Si hay filtros, se usan redirecciones, DNS rebinding, IPv6 o representaciones alternativas de IP.

## Variantes

- **SSRF básica**: respuesta reflejada.
- **Blind SSRF**: sin respuesta, se confirma con listener.
- **Metadata cloud**: credenciales temporales.
- **Gopher**: interacción con protocolos internos.
- **DNS rebinding**: evita allowlists.

## Limitaciones

- El backend puede bloquear IPs privadas.
- Puede requerir autenticación.
- La respuesta puede no reflejarse.
- Los metadatos pueden exigir cabeceras.

## Mitigación

- Allowlist de dominios y esquemas.
- Resolver DNS y validar la IP final.
- Bloquear rangos privados y metadata.
- Aislar el servicio que hace peticiones.

## Detección

- Peticiones a `localhost`/IPs privadas desde servidores.
- Conexiones a metadata cloud.
- URLs con redirecciones o esquemas raros.
- Picos desde un usuario.

MITRE ATT&CK: T1190 (Exploit Public-Facing Application), T1552.005 (Cloud Instance Metadata API).

## Referencias

- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://attack.mitre.org/techniques/T1552/005/>
- <https://github.com/swisskyrepo/PayloadsAllTheThings>
