---
topic: Recovering a JWT RSA key
tags: [web, jwt, rsa, cryptography, authentication]
---

# Recovering a JWT RSA key

[🌐 Español](jwt-rsa-key-recovery.md) | **English**

## Concept

An RSA-signed JWT is verified with a public key. If the key is weak or shipped with the code, the private key can be recovered and used to sign administrator tokens.

## When it applies

- The JWT uses `RS256`.
- The public key is in the repository or an accessible `kid`.
- The key is short or shares primes.

## Procedure

1. Extract the public key.
2. Run `RsaCtfTool` or `rsactftool` to recover the private key.
3. Sign a token with `role=admin`.
4. Use the token in the cookie.

```bash
RsaCtfTool --publickey public.pem --private
python3 jwt_tool.py <TOKEN> -S rs256 -priv private.pem -I -pc role -pv admin
```

## Variants

- Try `alg:none` if the library accepts it.
- Point `kid` at a controlled path.
- Use the key to decrypt other data.

## Limitations

- The key must be recoverable.
- The server must accept the signed token.
- The role must exist in the application.

## Mitigation and detection

- Use RSA keys of 2048 bits or more.
- Never publish private keys or trust external `kid`.
- Validate algorithm and claims server-side.

## References

- <https://datatracker.ietf.org/doc/html/rfc7519>
- <https://github.com/RsaCtfTool/RsaCtfTool>
- <https://attack.mitre.org/techniques/T1550/>
