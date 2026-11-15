---
topic: Blazor — forja de JWT con el secreto del cliente
tags: [windows, blazor, jwt, hmac, secret]
---

# Blazor — forja de JWT con el secreto del cliente

[🌐 English](blazor-jwt-forgery.en.md) | **Español**

## Concepto

Una aplicación Blazor WebAssembly descarga sus DLL al navegador. Si el secreto HMAC para firmar JWT está embebido en el cliente, cualquiera puede leerlo y firmar un token con el rol que quiera. El servidor solo comprueba la firma y confía en los claims.

## Cuándo aplica

- La app usa JWT HS256 y el secreto viaja en el ensamblado del cliente.
- El panel confía en el claim de rol sin consultar el servidor.
- Se dispone de las DLL de `_framework`.

## Procedimiento

1. Descargar las DLL de Blazor desde `/_framework/`.
2. Buscar cadenas y constantes que parezcan claves.
3. Forjar un JWT con el rol de administrador.
4. Usar el token en la API o el panel.

## Comandos

```bash
curl -s http://<HOST>/_framework/Blazorized.Client.dll -o client.dll
strings -el client.dll | grep -iE "secret|key|jwt|hmac"
python3 jwt_tool.py <TOKEN> -S hs256 -p "<SECRET>"
# Alternativa con PyJWT
python3 -c "import jwt; print(jwt.encode({'role':'admin'}, '<SECRET>', algorithm='HS256'))"
```

## Variantes

- Modificar el claim de usuario o de tenant, no solo el rol.
- Probar el secreto en cookies o tokens de otros servicios.
- Usar `jwt_tool` para probar `alg:none` si el servidor lo acepta.

## Limitaciones

- Si el servidor usa RS256 y valida la clave pública, el secreto no sirve.
- El token puede tener caducidad o audiencia estricta.
- La DLL puede estar ofuscada y requerir búsqueda adicional.

## Mitigación

- Firmar JWT en el servidor con una clave que nunca llegue al cliente.
- Preferir RS256/ES256 y validar `aud`, `iss` y expiración.
- No confiar en roles del token sin autorización del servidor.

## Detección

- Tokens con firma válida pero claims incoherentes.
- Uso de la misma cuenta desde ubicaciones distintas.
- Descargas repetidas de DLL de Blazor seguidas de acceso admin.

## Referencias

- [Microsoft — JWT validation](https://learn.microsoft.com/en-us/entra/identity-platform/security-tokens)
- [0xdf — Blazorized](https://0xdf.gitlab.io/2024/11/09/htb-blazorized.html)
- [CWE-798 — Hard-coded Credentials](https://cwe.mitre.org/data/definitions/798.html)
