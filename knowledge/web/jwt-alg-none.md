---
topic: JWT alg none
tags: [web, jwt, authentication-bypass, alg-none]
---

# JWT alg none

[🇬🇧 English](jwt-alg-none.en.md) | **Español**

## Concepto

Un JWT tiene tres partes: header, payload y firma. Si el servidor acepta el algoritmo `none`, ignora la firma y confía en los claims del payload. Un atacante puede cambiar `role`/`user` y entrar como administrador.

## Cuándo aplica

- La aplicación usa JWT y una librería antigua o mal configurada.
- El servidor no fija los algoritmos permitidos.
- El claim de rol se usa para autorizar sin validación adicional.

## Requisitos

1. Un JWT válido de usuario normal.
2. Conocer la estructura del payload.
3. Cliente HTTP para reenviar el token.

## Procedimiento

Se decodifica el payload:

```bash
echo '<jwt>' | cut -d. -f2 | base64 -d
```

Se construye un header con `alg:none`, se modifica el rol y se deja la firma vacía:

```json
{"alg":"none","typ":"JWT"}
{"user":"<user>","role":"admin"}
```

```bash
python3 jwt_tool.py <jwt> -X a
```

Se envía el token en la cookie o cabecera `Authorization` y se accede al panel.

## Variantes

- **`none` en mayúsculas/minúsculas**: `None`, `NONE`.
- **Confusión de algoritmos**: RS256 → HS256 usando la clave pública.
- **Clave débil**: crackear HS256 con diccionario.
- **`kid` injection**: path traversal o SQLi en el identificador de clave.

## Limitaciones

- Librerías modernas rechazan `none`.
- El servidor puede validar el rol contra la base de datos.
- Puede requerir una firma válida aunque el algoritmo sea débil.

## Mitigación

- Fijar algoritmos permitidos (`RS256`) y verificar firma.
- Rechazar `none` explícitamente.
- Validar roles en el servidor.
- Rotar claves y usar librerías actualizadas.

## Detección

- JWT con header `alg:none`.
- Tokens con firma vacía o inválida.
- Cambios de rol en el payload.
- Picos de acceso a endpoints admin.

MITRE ATT&CK: T1550 (Use Alternate Authentication Material), T1078 (Valid Accounts).

## Referencias

- <https://datatracker.ietf.org/doc/html/rfc8725>
- <https://owasp.org/www-project-web-security-testing-guide/>
- <https://github.com/ticarpi/jwt_tool>
