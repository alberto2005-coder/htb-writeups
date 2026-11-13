---
topic: IDOR
tags: [web, api, idor, authorization, access-control, burp]
---

# IDOR

**English** | [🇪🇸 Español](idor.md)

## Concept

Insecure Direct Object Reference occurs when an API accepts an object identifier and does not verify that the authenticated user has permission over it. Changing a number, UUID or resource name can reveal another account's data or allow administrative actions.

## When it applies

- Endpoints with `id`, `user_id`, `account` or UUID.
- Panels with shared objects.
- APIs trusting the client-supplied identifier.
- Read, edit or delete operations.

## Procedure

1. Create two accounts with different permissions.
2. Capture an authenticated request.
3. Replace the identifier with the other account's.
4. Compare status, length and content.
5. Test other methods and hidden fields too.

```bash
curl -s -H 'Authorization: Bearer <TOKEN_A>' https://<HOST>/api/users/1001
curl -s -H 'Authorization: Bearer <TOKEN_A>' https://<HOST>/api/users/1002
```

## Variants

- Horizontal IDOR between users of the same role.
- Vertical IDOR into administrator functions.
- Mass assignment of `role` or `owner`.
- UUID enumeration and deleted objects.

## Limitations

- The server must use the identifier without checking ownership.
- Random UUIDs make enumeration harder.
- Some responses hide data but still allow actions.
- Rate limiting can block bulk testing.

## Mitigation and detection

- Authorize per object on the server, not by hiding IDs.
- Use opaque identifiers and check ownership.
- Apply field allowlists.
- Alert on access to other accounts' objects and role changes.

## References

- <https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control>
- <https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html>
- <https://portswigger.net/web-security/access-control/idor>
