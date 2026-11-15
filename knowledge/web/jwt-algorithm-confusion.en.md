---
topic: JWT — RS256/HS256 algorithm confusion
tags: [web, jwt, algorithm-confusion, rs256, hs256]
---

# JWT — RS256/HS256 algorithm confusion

**English** | [🌐 Español](jwt-algorithm-confusion.md)

## Concept

If the server chooses the algorithm from the token header, an RS256 token can be changed to HS256 and signed with the public key. The library verifies the HMAC using that public key as the secret, and the token is accepted.

## When it applies

- The app uses asymmetric JWT and publishes the public key (JWKS).
- The code passes token and key to `verify` without pinning the algorithm.
- Header and payload can be modified.

## Procedure

1. Get the public key from JWKS or the repository.
2. Change `alg` to HS256 and raise the role.
3. Sign with the public key as the secret.
4. Send the token and verify access.

## Commands

```bash
python3 jwt_tool.py -S hs256 -k public.pem -I -pc role -pv admin <TOKEN>
curl -H 'x-access-token: <NEW>' http://api/webhooks
```

## Variants

- `kid` path traversal or injection.
- Public key from `.well-known/jwks.json`.
- `none` signing if accepted.

## Limitations

- A library pinned to RS256 rejects HS256.
- The public key must be in the expected format.
- The server may validate `iss`/`aud`.

## Mitigation

- Pin the expected algorithm and reject others.
- Validate `kid`, `iss`, `aud` and expiry.
- Never use the public key as an HMAC secret.

## Detection

- Tokens with changed `alg` or unexpected HMAC.
- Requests with elevated roles from the same user.
- JWKS access followed by token use.

## References

- [0xdf — CyberMonday](https://0xdf.gitlab.io/2023/12/02/htb-cybermonday.html)
- [PortSwigger — JWT algorithm confusion](https://portswigger.net/web-security/jwt/algorithm-confusion)
- [RFC 7519 — JWT](https://www.rfc-editor.org/rfc/rfc7519)
