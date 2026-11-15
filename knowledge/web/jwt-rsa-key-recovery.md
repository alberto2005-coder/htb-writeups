---
topic: Recuperación de la clave RSA de un JWT
tags: [web, jwt, rsa, cryptography, authentication]
---

# Recuperación de la clave RSA de un JWT

[🌐 English](jwt-rsa-key-recovery.en.md) | **Español**

## Concepto

Un JWT firmado con RSA se valida con una clave pública. Si la clave es débil o se distribuye junto al código, se puede recuperar la privada y firmar tokens con el rol de administrador.

## Cuándo aplica

- El JWT usa `RS256`.
- La clave pública está en el repositorio o en un `kid` accesible.
- La clave es corta o comparte primos.

## Procedimiento

1. Extraer la clave pública.
2. Ejecutar `RsaCtfTool` o `rsactftool` para recuperar la privada.
3. Firmar un token con `role=admin`.
4. Usar el token en la cookie.

```bash
RsaCtfTool --publickey public.pem --private
python3 jwt_tool.py <TOKEN> -S rs256 -priv private.pem -I -pc role -pv admin
```

## Variantes

- Probar `alg:none` si la librería lo acepta.
- Cambiar `kid` por una ruta controlada.
- Usar la clave para descifrar otros datos.

## Limitaciones

- La clave debe ser recuperable.
- El servidor debe aceptar el token firmado.
- El rol debe existir en la aplicación.

## Mitigación y detección

- Usar claves RSA de 2048 bits o más.
- No publicar claves privadas ni confiar en `kid` externo.
- Validar algoritmo y claims en el servidor.

## Referencias

- <https://datatracker.ietf.org/doc/html/rfc7519>
- <https://github.com/RsaCtfTool/RsaCtfTool>
- <https://attack.mitre.org/techniques/T1550/>
