---
topic: JWT — confusión de algoritmos RS256/HS256
tags: [web, jwt, algorithm-confusion, rs256, hs256]
---

# JWT — confusión de algoritmos RS256/HS256

[🌐 English](jwt-algorithm-confusion.en.md) | **Español**

## Concepto

Si el servidor elige el algoritmo según el header del token, un token RS256 puede convertirse en HS256 y firmarse con la clave pública. La biblioteca verifica la firma HMAC usando esa clave pública como secreto, y el token se acepta.

## Cuándo aplica

- La aplicación usa JWT asimétrico y publica la clave pública (JWKS).
- El código pasa el token y la clave a `verify` sin fijar el algoritmo.
- Se puede modificar el header y el payload.

## Procedimiento

1. Obtener la clave pública desde JWKS o el repositorio.
2. Cambiar `alg` a HS256 y elevar el rol.
3. Firmar con la clave pública como secreto.
4. Enviar el token y comprobar el acceso.

## Comandos

```bash
python3 jwt_tool.py -S hs256 -k public.pem -I -pc role -pv admin <TOKEN>
curl -H 'x-access-token: <NEW>' http://api/webhooks
```

## Variantes

- `kid` con path traversal o inyección.
- Clave pública recuperada de `.well-known/jwks.json`.
- Firma con `none` si se acepta.

## Limitaciones

- Una biblioteca que fija RS256 rechaza HS256.
- La clave pública debe estar en el formato esperado.
- El servidor puede validar `iss`/`aud`.

## Mitigación

- Fijar el algoritmo esperado y rechazar otros.
- Validar `kid`, `iss`, `aud` y expiración.
- No usar la clave pública como secreto HMAC.

## Detección

- Tokens con `alg` cambiado o firma HMAC inesperada.
- Peticiones con roles elevados desde el mismo usuario.
- Accesos a JWKS seguidos de uso de tokens.

## Referencias

- [0xdf — CyberMonday](https://0xdf.gitlab.io/2023/12/02/htb-cybermonday.html)
- [PortSwigger — JWT algorithm confusion](https://portswigger.net/web-security/jwt/algorithm-confusion)
- [RFC 7519 — JWT](https://www.rfc-editor.org/rfc/rfc7519)
