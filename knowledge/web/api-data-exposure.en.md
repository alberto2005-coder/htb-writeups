---
topic: API data exposure
tags: [web, api, data-exposure, hashes, backups, enumeration]
---

# API data exposure

**English** | [🇪🇸 Español](api-data-exposure.md)

## Concept

An API returns more fields than needed or serves objects that should be internal. A user endpoint may include hashes, tokens, emails, roles or backup paths. The problem is not only access, but how much sensitive data is returned.

## When it applies

- JSON endpoints for users, orders or settings.
- Responses containing `password`, `hash`, `token`, `internal_id` or `path`.
- Backup directories reachable from the web root.
- APIs without per-role field control.

## Procedure

1. Enumerate routes and methods with `ffuf`, `feroxbuster` or browser history.
2. Review each response and note sensitive fields.
3. Compare a normal user's response with an administrator's.
4. Look for backup files and metadata in common paths.
5. Test whether the hashes are crackable or reusable.

```bash
curl -s https://<HOST>/api/users/latest | jq '.[0] | keys'
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://<HOST>/backup.zip
```

## Variants

- Password hash in the response and offline cracking.
- Backup path containing source and credentials.
- Manipulable `role` or `is_admin` field.
- Sequential ID enumeration without authorization.

## Limitations

- The hash must use a weak or reused algorithm.
- Backups may sit outside the web directory.
- Some fields only appear with specific parameters.
- Rate limiting and authentication can slow enumeration.

## Mitigation and detection

- Use DTOs and per-role field allowlists.
- Never return hashes, tokens or internal paths.
- Keep backups outside the web root and require authentication.
- Alert on ZIP/SQL downloads and user enumeration.

## References

- <https://owasp.org/www-project-api-security/>
- <https://cwe.mitre.org/data/definitions/213.html>
- <https://attack.mitre.org/techniques/T1213/>
- <https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html>
