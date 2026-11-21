---
topic: pac4j-jwt — bypass con JWT cifrado (CVE-2026-29000)
tags: [web, pac4j, jwt, jwe, cve-2026-29000, spring-boot, principal]
---

# pac4j-jwt — bypass con JWT cifrado (CVE-2026-29000)

[🌐 English](pac4j-jwt-auth-bypass.en.md) | **Español**

## Concepto

pac4j-jwt anterior a 4.5.9, 5.7.9 y 6.3.3 procesa JWT cifrados (JWE) sin validar correctamente la firma. Un atacante puede cifrar un token con la clave pública RSA del servidor y un `sub` arbitrario; el servidor lo descifra con su clave privada y acepta la identidad sin comprobar la firma. En Principal, la aplicación Spring Boot exponía el JWKS y permitía forjar un token de administrador con la CVE-2026-29000.

## Cuándo aplica

- Aplicación Java con pac4j-jwt en una versión afectada.
- El JWKS o la clave pública RSA es accesible.
- La aplicación acepta JWT cifrados además de firmados.
- El `sub` o los roles no se validan contra el emisor.

## Procedimiento

1. Identificar la versión de pac4j y el endpoint JWKS.
2. Obtener la clave pública RSA (`n`, `e`).
3. Construir un JWE con `alg` y `enc` aceptados por el servidor.
4. Incluir un `sub` y roles privilegiados.
5. Enviar el token y comprobar el acceso.
6. Usar el panel para obtener credenciales o ejecutar acciones.

## Comandos

```bash
curl -s http://<HOST>:8080/<JWKS_PATH> | jq
```

```python
# Esquema: cifrar con la clave pública; el servidor vulnerable no valida la firma interna
from jwcrypto import jwk, jwt
public_jwk = {"kty": "RSA", "n": "<N>", "e": "AQAB"}  # clave del JWKS
key = jwk.JWK(**public_jwk)
token = jwt.JWT(header={"alg": "RSA-OAEP", "enc": "A256GCM"},
                claims={"sub": "admin", "role": "admin"})
token.make_encrypted_token(key)
print(token.serialize())
```

## Variantes

- Cambiar `alg`/`enc` según lo que acepte la librería.
- Usar un `kid` conocido para seleccionar la clave.
- Añadir grupos o `scope` si la autorización los usa.
- Reutilizar el token en otras rutas de la misma aplicación.
- Combinar con un password spray si el panel filtra credenciales.

## Limitaciones

- Las versiones corregidas validan la firma aunque el token esté cifrado.
- El JWKS debe ser accesible y la clave compatible.
- La aplicación debe aceptar JWE; si solo acepta JWS, no aplica.
- Los claims pueden validarse contra el emisor.
- El token puede caducar y requerir renovación.

## Mitigación

- Actualizar pac4j-jwt a 4.5.9, 5.7.9, 6.3.3 o posterior.
- Validar firma, `iss`, `aud`, `exp` y algoritmo en todos los tokens.
- No aceptar JWE de emisores no confiables.
- Restringir el JWKS y monitorizar su consulta.
- Aplicar autorización por rol y por objeto.

## Detección

- Consultas al JWKS desde IPs externas.
- Tokens con `alg`/`enc` inusuales o `kid` desconocidos.
- Accesos a paneles con `sub` que no coincide con el emisor.
- Errores de validación de firma ausentes en los logs.
- Versiones de pac4j afectadas en el inventario.

## Referencias

- [NVD — CVE-2026-29000](https://nvd.nist.gov/vuln/detail/CVE-2026-29000)
- [0xdf — Principal](https://0xdf.gitlab.io/2026/03/30/htb-principal.html)
- [pac4j — Documentación](https://www.pac4j.org/docs/)
- [Ficha Principal](../../machines/linux/principal/README.md)
