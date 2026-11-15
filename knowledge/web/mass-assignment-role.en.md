---
title: Mass assignment — turning a profile into admin
tags: [web, mass-assignment, authorization, json, privesc]
---

# Mass assignment — turning a profile into admin

[🇪🇸 Español](mass-assignment-role.md) | **English**

## Concept

Mass assignment happens when the server copies every request field into the model without filtering. If the object accepts `role`, `is_admin` or `permissions`, the user can change their own privilege level.

## When it applies

- The profile is updated with JSON or forms and the server uses `Model.new(params)` or `update(params)`.
- The response includes role fields or the frontend sends them.
- There is no field allowlist.

## Procedure

1. Capture the registration or profile update request.
2. Add `"role":"admin"`, `"is_admin":true` or `"permissions":["admin"]`.
3. Check access to the panel or new functions.
4. If the field is nested, try `user[role]`, `roles[]` or duplicates.

```json
{"username":"demo","email":"demo@htb","role":"admin"}
```

```http
PATCH /api/profile HTTP/1.1
Content-Type: application/json

{"role":"admin"}
```

## Variants

- In Rails, `permit!` or a misconfigured `attr_accessible`.
- In Laravel, incomplete `$fillable` or `$guarded = []`.
- In Java/Spring, `@ModelAttribute` without `@InitBinder`.
- In Node, `Object.assign(user, req.body)`.

## Limitations

- The field may be ignored or validated server-side.
- Some frameworks separate the input model from the persistence model.
- The response may not reveal the role until re-authentication.

## Mitigation and detection

- Use DTOs and explicit allowlists.
- Never accept roles or permissions from the client.
- Audit role changes and separate profile updates from administrative ones.
- Test extra fields on every write endpoint.

## References

- <https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html>
- <https://cwe.mitre.org/data/definitions/915.html>
- <https://portswigger.net/web-security/access-control>
