---
topic: JWT alg none
tags: [web, jwt, authentication-bypass, alg-none]
---

# JWT alg none

**English** | [🇪🇸 Español](jwt-alg-none.md)

## Concept

A JWT has three parts: header, payload and signature. If the server accepts the `none` algorithm, it ignores the signature and trusts the payload claims. An attacker can change `role`/`user` and become administrator.

## When it applies

- The application uses JWT with an old or misconfigured library.
- The server does not pin allowed algorithms.
- The role claim authorises without further validation.

## Requirements

1. A valid JWT from a normal user.
2. Knowledge of the payload structure.
3. An HTTP client to resend the token.

## Procedure

Decode the payload:

```bash
echo '<jwt>' | cut -d. -f2 | base64 -d
```

Build a header with `alg:none`, change the role and leave the signature empty:

```json
{"alg":"none","typ":"JWT"}
{"user":"<user>","role":"admin"}
```

```bash
python3 jwt_tool.py <jwt> -X a
```

Send the token in the cookie or `Authorization` header and access the panel.

## Variants

- **`none` casing**: `None`, `NONE`.
- **Algorithm confusion**: RS256 → HS256 using the public key.
- **Weak key**: crack HS256 with a wordlist.
- **`kid` injection**: path traversal or SQLi in the key identifier.

## Limitations

- Modern libraries reject `none`.
- The server may validate the role against the database.
- A valid signature may still be required even with a weak algorithm.

## Mitigation

- Pin allowed algorithms (`RS256`) and verify signatures.
- Explicitly reject `none`.
- Validate roles server-side.
- Rotate keys and use updated libraries.

## Detection

- JWT with header `alg:none`.
- Tokens with empty or invalid signatures.
- Role changes in the payload.
- Spikes in admin endpoint access.

MITRE ATT&CK: T1550 (Use Alternate Authentication Material), T1078 (Valid Accounts).

## References

- <https://datatracker.ietf.org/doc/html/rfc8725>
- <https://owasp.org/www-project-web-security-testing-guide/>
- <https://github.com/ticarpi/jwt_tool>
