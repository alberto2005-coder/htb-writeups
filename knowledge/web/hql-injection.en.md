---
topic: HQL — injection in Hibernate queries
tags: [web, hibernate, hql, injection, java, fingerprint]
---

# HQL — injection in Hibernate queries

**English** | [🌐 Español](hql-injection.md)

## Idea

Hibernate Query Language (HQL) queries Java entities, not SQL tables. When an application concatenates user input into an HQL query, conditions can be altered and data extracted with boolean injection. The syntax is not SQL: it uses entity and property names, and comments and functions differ. On Fingerprint, an HQL query built from the username enumerated records and hidden fields.

## When it applies

- A Java application using Hibernate builds HQL by concatenation.
- The parameter is used in `WHERE`, `ORDER BY` or `LIKE`.
- The response changes with the condition (boolean-based).
- Error messages or timing differences are usable.

## Procedure

1. Identify the entity and property used in the query.
2. Test single quotes and logical operators.
3. Confirm with a true and a false condition.
4. Extract data character by character with `SUBSTRING` and comparisons.
5. Adjust case and entity property names.
6. Reuse the data to authenticate or escalate.

## Commands

```text
' OR '1'='1
' AND SUBSTRING((SELECT u.password FROM User u WHERE u.username='admin'),1,1)='a'--
```

```bash
# Repeat the request for each character and measure the response
ffuf -u 'http://<HOST>/<PATH>?q=<PAYLOAD>' -w chars.txt -mr '<TRUE_MARKER>'
```

## Variants

- Injection in `ORDER BY` to infer columns.
- HQL functions such as `SUBSTRING`, `LOWER`, `CONCAT` and `COALESCE`.
- Blind timing injection with database functions.
- Access related entities through property navigation.
- Combine with deserialization or JWT to execute code.

## Limitations

- HQL does not accept every SQL construct; syntax must be adapted.
- Hibernate may parameterize or validate the query.
- Errors may be hidden and injection may be blind only.
- Entities and properties must be known or inferred.
- Queries are recorded in application logs.

## Mitigation

- Use parameterized queries (`setParameter`) and never concatenate input.
- Validate types and allowlists for sorting and filters.
- Do not expose Hibernate errors to users.
- Review code that builds HQL dynamically.
- Enforce per-object authorization in queries.

## Detection

- Parameters with quotes, `OR`, `AND`, `SUBSTRING` or HQL comments.
- Queries with anomalous response times.
- Hibernate errors in HTTP responses.
- Repeated requests varying a single character.
- Queries returning more entities than expected.

## References

- [0xdf — Fingerprint](https://0xdf.gitlab.io/2022/05/14/htb-fingerprint.html)
- [Hibernate — HQL](https://docs.jboss.org/hibernate/orm/6.2/userguide/html_single/Hibernate_User_Guide.html#hql)
- [Fingerprint writeup](../../machines/linux/fingerprint/README.en.md)
