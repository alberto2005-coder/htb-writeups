---
topic: Blazor — JWT forgery with the client secret
tags: [windows, blazor, jwt, hmac, secret]
---

# Blazor — JWT forgery with the client secret

**English** | [🌐 Español](blazor-jwt-forgery.md)

## Concept

A Blazor WebAssembly application downloads its DLLs to the browser. If the HMAC secret used to sign JWTs is embedded in the client, anyone can read it and sign a token with any role. The server only checks the signature and trusts the claims.

## When it applies

- The app uses HS256 JWTs and the secret ships in the client assembly.
- The panel trusts the role claim without a server-side check.
- The `_framework` DLLs are available.

## Procedure

1. Download the Blazor DLLs from `/_framework/`.
2. Search strings and constants for key-like values.
3. Forge a JWT with the administrator role.
4. Use the token against the API or panel.

## Commands

```bash
curl -s http://<HOST>/_framework/Blazorized.Client.dll -o client.dll
strings -el client.dll | grep -iE "secret|key|jwt|hmac"
python3 jwt_tool.py <TOKEN> -S hs256 -p "<SECRET>"
# Alternative with PyJWT
python3 -c "import jwt; print(jwt.encode({'role':'admin'}, '<SECRET>', algorithm='HS256'))"
```

## Variants

- Modify the user or tenant claim, not just the role.
- Try the secret on cookies or tokens of other services.
- Use `jwt_tool` to test `alg:none` if the server accepts it.

## Limitations

- If the server uses RS256 and validates the public key, the secret is useless.
- The token may have strict expiry or audience checks.
- The DLL may be obfuscated and require further searching.

## Mitigation

- Sign JWTs server-side with a key that never reaches the client.
- Prefer RS256/ES256 and validate `aud`, `iss` and expiry.
- Do not trust token roles without server-side authorization.

## Detection

- Validly signed tokens with inconsistent claims.
- The same account used from different locations.
- Repeated Blazor DLL downloads followed by admin access.

## References

- [Microsoft — JWT validation](https://learn.microsoft.com/en-us/entra/identity-platform/security-tokens)
- [0xdf — Blazorized](https://0xdf.gitlab.io/2024/11/09/htb-blazorized.html)
- [CWE-798 — Hard-coded Credentials](https://cwe.mitre.org/data/definitions/798.html)
