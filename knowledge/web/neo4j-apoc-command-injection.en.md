---
topic: Neo4j — APOC extension command injection
tags: [web, neo4j, cypher, apoc, java, command-injection]
---

# Neo4j — APOC extension command injection

**English** | [🌐 Español](neo4j-apoc-command-injection.md)

## Concept

A custom APOC extension may expose procedures that take a URL and concatenate it into a shell command. If the JAR is downloadable, reverse it to find the vulnerable method and call it from Cypher.

## When it applies

- The app uses Neo4j with custom extensions.
- The JAR or its docs are accessible.
- A procedure takes a URL and calls `curl` or `wget`.

## Procedure

1. Download the JAR and list classes.
2. Decompile and search for `Runtime.exec`, `/bin/sh` or `ProcessBuilder`.
3. Call the procedure with a URL that terminates the command.
4. Stabilize the shell and enumerate credentials.

## Commands

```bash
unzip -l custom-apoc-extension.jar
# decompile the procedure class
```

```cypher
CALL custom.getUrlStatusCode("neo4j.local; id; ") YIELD statusCode RETURN statusCode;
```

## Variants

- Injection in a configuration parameter.
- `curl` with multiple URLs or `file://`.
- Procedures writing files to controlled paths.

## Limitations

- The procedure may use an argument list.
- The JAR may not be accessible.
- Neo4j may restrict procedures to admins.

## Mitigation

- Do not concatenate input into shell commands.
- Use native HTTP APIs and allowlists.
- Sign and review extensions; do not publish internal JARs.

## Detection

- Custom APOC procedures in the query log.
- Outbound connections from the Neo4j process.
- Child shells spawned by Java.

## References

- [0xdf — Cypher](https://0xdf.gitlab.io/2025/07/26/htb-cypher.html)
- [Neo4j — APOC](https://neo4j.com/docs/apoc/current/)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
