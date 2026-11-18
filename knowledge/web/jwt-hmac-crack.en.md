---
topic: JWT HS256 — cracking and forging the secret
tags: [web, jwt, hmac, hashcat, authentication, awkward]
---

# JWT HS256 — cracking and forging the secret

[🌐 Español](jwt-hmac-crack.md) | **English**

## Idea

A JWT signed with HS256 uses a symmetric key for the HMAC. If the secret is weak, it can be recovered offline with a wordlist and used to sign custom tokens with arbitrary claims. There is no need to break the algorithm: guessing the key is enough. On Awkward an API token was captured, its secret cracked and requests signed to read files.

## When it applies

- The token is a JWT with `"alg":"HS256"` or `HS384`/`HS512`.
- The secret is short, default or present in a wordlist.
- The application trusts token claims without checking state server-side.
- An endpoint returns a valid token to start from.

## Procedure

1. Capture a JWT from a cookie, `Authorization` header or response.
2. Check the algorithm and decode the payload.
3. Crack the secret with `hashcat` or `john`.
4. Sign a new token with modified claims.
5. Send it to the protected endpoint.

## Commands

```bash
# mode 16500 = JWT HS256
hashcat -m 16500 token.txt /usr/share/wordlists/rockyou.txt
john --format=HMAC-SHA256 token.txt --wordlist=rockyou.txt
```

```python
import jwt
token = jwt.encode({"username": "admin", "role": "admin"}, "<SECRET>", algorithm="HS256")
print(token)
```

```bash
curl -s http://<HOST>/<PATH> -H "Authorization: Bearer <TOKEN>"
```

## Variants

- Try common secrets first (`secret`, `changeme`, the app name).
- If the server accepts `alg: none`, try that variant too.
- With an RSA public key and a confused `alg`, use the public key as the HMAC secret.
- If the token expires, adjust `exp` and `iat` when signing the new one.

## Limitations

- A long, random secret will not fall to a wordlist.
- The application may verify against a key list and rotate it.
- Some frameworks also validate `iss`, `aud` or `kid`.
- Offline cracking leaves no traffic on the server.

## Mitigation

- Use long, random secrets kept in a manager and rotated.
- Prefer asymmetric algorithms when issuer and verifier differ.
- Pin the expected algorithm and reject `none` and `alg` changes.
- Validate `iss`, `aud`, `exp` and server-side session state.
- Limit token lifetime and allow revocation.

## Detection

- Tokens whose `alg` differs from the configured one.
- Claim changes without a prior issuance.
- Requests with tokens signed by a recovered secret from new IPs.
- Brute force against the token-issuing endpoint.

## References

- [OWASP — JSON Web Token Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [PortSwigger — JWT attacks](https://portswigger.net/web-security/jwt)
- [0xdf — Awkward](https://0xdf.gitlab.io/2023/02/25/htb-awkward.html)
- [Awkward writeup](../../machines/linux/awkward/README.en.md)
