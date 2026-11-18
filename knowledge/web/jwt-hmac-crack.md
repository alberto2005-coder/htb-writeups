---
topic: JWT HS256 — crackeo y falsificación del secreto
tags: [web, jwt, hmac, hashcat, autenticacion, awkward]
---

# JWT HS256 — crackeo y falsificación del secreto

[🌐 English](jwt-hmac-crack.en.md) | **Español**

## Concepto

Un JWT firmado con HS256 usa una clave simétrica para el HMAC. Si el secreto es débil, se puede recuperar offline con un diccionario y después firmar tokens propios con los claims que interesen. No hace falta romper el algoritmo: basta con adivinar la clave. En Awkward se capturó un token de la API, se crackeó su secreto y se firmaron peticiones para leer archivos.

## Cuándo aplica

- El token es un JWT con `"alg":"HS256"` o `HS384`/`HS512`.
- El secreto es corto, por defecto o está en una lista de diccionario.
- La aplicación confía en los claims del token sin comprobar el estado en el servidor.
- Hay un endpoint que devuelve un token válido para empezar.

## Procedimiento

1. Capturar un JWT de una cookie, cabecera `Authorization` o respuesta.
2. Verificar el algoritmo y decodificar el payload.
3. Crackear el secreto con `hashcat` o `john`.
4. Firmar un token nuevo con los claims modificados.
5. Enviarlo al endpoint protegido.

## Comandos

```bash
# modo 16500 = JWT HS256
hashcat -m 16500 token.txt /usr/share/wordlists/rockyou.txt
john --format=HMAC-SHA256 token.txt --wordlist=rockyou.txt
```

```python
import jwt
token = jwt.encode({"username": "admin", "role": "admin"}, "<SECRETO>", algorithm="HS256")
print(token)
```

```bash
curl -s http://<HOST>/<RUTA> -H "Authorization: Bearer <TOKEN>"
```

## Variantes

- Probar primero secretos comunes (`secret`, `changeme`, el nombre de la app).
- Si el servidor acepta `alg: none`, probar también esa variante.
- Con una clave pública RSA y `alg` confundido, usar la clave pública como secreto HMAC.
- Si el token caduca, ajustar `exp` y `iat` al firmar el nuevo.

## Limitaciones

- Un secreto largo y aleatorio no se recupera por diccionario.
- La aplicación puede comprobar la firma contra una lista de claves y rotar.
- Algunos frameworks validan también `iss`, `aud` o el `kid`.
- El crackeo offline no deja tráfico en el servidor.

## Mitigación

- Usar secretos largos y aleatorios, guardados en un gestor y rotados.
- Preferir algoritmos asimétricos cuando el emisor y el verificador son distintos.
- Fijar el algoritmo esperado y rechazar `none` y cambios de `alg`.
- Validar `iss`, `aud`, `exp` y el estado de la sesión en el servidor.
- Limitar la vida del token y permitir revocación.

## Detección

- Tokens con `alg` distinto del configurado.
- Cambios de claims sin una emisión previa.
- Peticiones con tokens firmados por un secreto recuperado, desde IPs nuevas.
- Intentos de fuerza bruta contra el endpoint que emite tokens.

## Referencias

- [OWASP — JSON Web Token Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [PortSwigger — JWT attacks](https://portswigger.net/web-security/jwt)
- [0xdf — Awkward](https://0xdf.gitlab.io/2023/02/25/htb-awkward.html)
- [Ficha Awkward](../../machines/linux/awkward/README.md)
