---
topic: pac4j-jwt — auth bypass with an encrypted JWT (CVE-2026-29000)
tags: [web, pac4j, jwt, jwe, cve-2026-29000, spring-boot, principal]
---

# pac4j-jwt — auth bypass with an encrypted JWT (CVE-2026-29000)

**English** | [🌐 Español](pac4j-jwt-auth-bypass.md)

## Idea

pac4j-jwt before 4.5.9, 5.7.9 and 6.3.3 processes encrypted JWTs (JWE) without correctly validating the signature. An attacker encrypts a token with the server's RSA public key and an arbitrary `sub`; the server decrypts it with its private key and accepts the identity without checking the signature. On Principal, the Spring Boot application exposed the JWKS and allowed forging an administrator token via CVE-2026-29000.

## When it applies

- A Java application uses an affected pac4j-jwt version.
- The JWKS or RSA public key is reachable.
- The application accepts encrypted JWTs as well as signed ones.
- `sub` or roles are not validated against the issuer.

## Procedure

1. Identify the pac4j version and the JWKS endpoint.
2. Obtain the RSA public key (`n`, `e`).
3. Build a JWE with `alg` and `enc` accepted by the server.
4. Include a privileged `sub` and roles.
5. Send the token and check access.
6. Use the panel to obtain credentials or perform actions.

## Commands

```bash
curl -s http://<HOST>:8080/<JWKS_PATH> | jq
```

```python
# Outline: encrypt with the public key; the vulnerable server does not validate the inner signature
from jwcrypto import jwk, jwt
public_jwk = {"kty": "RSA", "n": "<N>", "e": "AQAB"}  # JWKS key
key = jwk.JWK(**public_jwk)
token = jwt.JWT(header={"alg": "RSA-OAEP", "enc": "A256GCM"},
                claims={"sub": "admin", "role": "admin"})
token.make_encrypted_token(key)
print(token.serialize())
```

## Variants

- Change `alg`/`enc` to what the library accepts.
- Use a known `kid` to select the key.
- Add groups or `scope` if authorization uses them.
- Reuse the token on other routes of the same application.
- Combine with a password spray if the panel leaks credentials.

## Limitations

- Fixed versions validate the signature even when the token is encrypted.
- The JWKS must be reachable and the key compatible.
- The application must accept JWE; JWS-only apps are unaffected.
- Claims may be validated against the issuer.
- The token may expire and require renewal.

## Mitigation

- Update pac4j-jwt to 4.5.9, 5.7.9, 6.3.3 or later.
- Validate signature, `iss`, `aud`, `exp` and algorithm on every token.
- Do not accept JWE from untrusted issuers.
- Restrict the JWKS and monitor its access.
- Enforce role and object-level authorization.

## Detection

- JWKS requests from external IPs.
- Tokens with unusual `alg`/`enc` or unknown `kid`.
- Panel access with a `sub` that does not match the issuer.
- Missing signature-validation errors in logs.
- Affected pac4j versions in the inventory.

## References

- [NVD — CVE-2026-29000](https://nvd.nist.gov/vuln/detail/CVE-2026-29000)
- [0xdf — Principal](https://0xdf.gitlab.io/2026/03/30/htb-principal.html)
- [pac4j — Documentation](https://www.pac4j.org/docs/)
- [Principal writeup](../../machines/linux/principal/README.en.md)
