---
topic: Inyección NoSQL en MongoDB
tags: [web, mongodb, nosql, injection, authentication]
---

# NoSQL Injection in MongoDB

**English** | [🇪🇸 Español](nosql-injection.md)

## Concept

MongoDB accepts documents and operators such as `$ne`, `$gt`, `$regex` or `$where`. If an application concatenates user-controlled objects into a query, authentication logic can be altered or data extracted.

## When it applies

- A login receives JSON and passes it directly to `findOne`.
- Search parameters are used as objects or arrays.
- Node.js/Express applications use `req.body` without type validation.

## Procedure

1. Send an object where a string is expected.
2. Try `{"$ne": null}` or `{"$ne": "x"}` as the password.
3. Confirm the role or session obtained.
4. In searches, try `$regex` to enumerate values.
5. Check whether `$where` allows JavaScript execution.

```json
{"username":"admin","password":{"$ne":"x"}}
```

## Variants

- Username injection with `$regex`.
- Arrays that alter `$in` or `$or`.
- `$where` with JavaScript when enabled.

## Limitations

- An ODM/validator may force strings.
- Parameterised queries or a strict schema block the attack.
- MongoDB may require authentication and least privilege.

## Mitigation

- Validate types and use a schema (Joi, Zod, Mongoose).
- Cast fields to strings before querying.
- Use `$eq` and parameters; reject keys starting with `$`.
- Restrict `$where` and database access.

## Detection

- JSON bodies with `$` keys.
- Driver type errors.
- Repeated object-based login attempts.
- Slow queries or unusual `$where`.

## References

- <https://owasp.org/www-community/attacks/NoSQL_Injection>
- <https://www.mongodb.com/docs/manual/reference/operator/query/>
- <https://attack.mitre.org/techniques/T1190/>
