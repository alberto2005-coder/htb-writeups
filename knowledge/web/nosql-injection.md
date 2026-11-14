---
topic: Inyección NoSQL en MongoDB
tags: [web, mongodb, nosql, injection, authentication]
---

# Inyección NoSQL en MongoDB

[🇬🇧 English](nosql-injection.en.md) | **Español**

## Concepto

MongoDB acepta documentos y operadores como `$ne`, `$gt`, `$regex` o `$where`. Si una aplicación concatena objetos controlados por el usuario en una consulta, se puede alterar la lógica de autenticación o extraer datos.

## Cuándo aplica

- Login que recibe JSON y lo pasa directamente a `findOne`.
- Parámetros de búsqueda usados como objetos o arrays.
- Aplicaciones Node.js/Express con `req.body` sin validación de tipo.

## Procedimiento

1. Enviar un objeto donde se espera una cadena.
2. Probar `{"$ne": null}` o `{"$ne": "x"}` en la contraseña.
3. Confirmar el rol o la sesión obtenida.
4. En búsquedas, probar `$regex` para enumerar valores.
5. Revisar si `$where` permite ejecutar JavaScript.

```json
{"username":"admin","password":{"$ne":"x"}}
```

## Variantes

- Inyección en el nombre de usuario con `$regex`.
- Arrays para alterar `$in` o `$or`.
- `$where` con JavaScript si el servidor lo permite.

## Limitaciones

- El servidor puede usar un ODМ/validador que fuerce cadenas.
- Las consultas parametrizadas o un esquema estricto bloquean el ataque.
- MongoDB puede tener autenticación y permisos limitados.

## Mitigación

- Validar tipos y usar un esquema (Joi, Zod, Mongoose).
- Convertir los campos a cadena antes de consultar.
- Usar `$eq` y parámetros; prohibir claves que empiecen por `$`.
- Limitar `$where` y el acceso a la base.

## Detección

- Cuerpos JSON con claves `$`.
- Errores de tipo en el driver.
- Intentos repetidos de login con objetos.
- Consultas lentas o `$where` inusuales.

## Referencias

- <https://owasp.org/www-community/attacks/NoSQL_Injection>
- <https://www.mongodb.com/docs/manual/reference/operator/query/>
- <https://attack.mitre.org/techniques/T1190/>
