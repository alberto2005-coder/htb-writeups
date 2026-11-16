---
topic: Neo4j — extensión APOC con inyección de comandos
tags: [web, neo4j, cypher, apoc, java, command-injection]
---

# Neo4j — extensión APOC con inyección de comandos

[🌐 English](neo4j-apoc-command-injection.en.md) | **Español**

## Concepto

Una extensión APOC personalizada puede exponer procedimientos que reciben una URL y la concatenan en una orden de shell. Si el JAR es descargable, se puede revertir para localizar el método vulnerable y llamarlo desde Cypher.

## Cuándo aplica

- La aplicación usa Neo4j con extensiones propias.
- El JAR o su documentación es accesible.
- Un procedimiento recibe una URL y llama a `curl` o `wget`.

## Procedimiento

1. Descargar el JAR y listar clases.
2. Descompilar y buscar `Runtime.exec`, `/bin/sh` o `ProcessBuilder`.
3. Invocar el procedimiento con una URL que cierre la orden.
4. Estabilizar la shell y enumerar credenciales.

## Comandos

```bash
unzip -l custom-apoc-extension.jar
# descompilar la clase del procedimiento
```

```cypher
CALL custom.getUrlStatusCode("neo4j.local; id; ") YIELD statusCode RETURN statusCode;
```

## Variantes

- Inyección en un parámetro de configuración.
- Uso de `curl` con varias URLs o `file://`.
- Procedimientos que escriben archivos en rutas controladas.

## Limitaciones

- El procedimiento puede usar una lista de argumentos.
- El JAR puede no estar accesible.
- Neo4j puede limitar los procedimientos a admin.

## Mitigación

- No concatenar entradas en órdenes de shell.
- Usar APIs HTTP nativas y listas blancas.
- Firmar y revisar extensiones; no publicar JARs internos.

## Detección

- Procedimientos APOC personalizados en el log de consultas.
- Conexiones salientes desde el proceso Neo4j.
- Shells hijas de Java.

## Referencias

- [0xdf — Cypher](https://0xdf.gitlab.io/2025/07/26/htb-cypher.html)
- [Neo4j — APOC](https://neo4j.com/docs/apoc/current/)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
