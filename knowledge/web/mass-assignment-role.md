---
title: Mass assignment — convertir el perfil en admin
tags: [web, mass-assignment, authorization, json, privesc]
---

# Mass assignment — convertir el perfil en admin

[🇬🇧 English](mass-assignment-role.en.md) | **Español**

## Concepto

Mass assignment ocurre cuando el servidor copia todos los campos de la petición al modelo sin filtrar. Si el objeto acepta `role`, `is_admin` o `permissions`, el usuario puede modificar su propio nivel de privilegio.

## Cuándo aplica

- El perfil se actualiza con JSON o formularios y el servidor usa `Model.new(params)` o `update(params)`.
- La respuesta incluye campos de rol o el frontend los envía.
- No hay una lista blanca de campos.

## Procedimiento

1. Capturar la petición de registro o actualización de perfil.
2. Añadir `"role":"admin"`, `"is_admin":true` o `"permissions":["admin"]`.
3. Comprobar el acceso al panel o a funciones nuevas.
4. Si el campo está anidado, probar `user[role]`, `roles[]` o duplicados.

```json
{"username":"demo","email":"demo@htb","role":"admin"}
```

```http
PATCH /api/profile HTTP/1.1
Content-Type: application/json

{"role":"admin"}
```

## Variantes

- En Rails, `permit!` o `attr_accessible` mal configurado.
- En Laravel, `$fillable` incompleto o `$guarded = []`.
- En Java/Spring, `@ModelAttribute` sin `@InitBinder`.
- En Node, `Object.assign(user, req.body)`.

## Limitaciones

- El campo puede ignorarse o validarse en el servidor.
- Algunos frameworks separan el modelo de entrada del de persistencia.
- La respuesta puede no revelar el rol hasta volver a autenticarse.

## Mitigación y detección

- Usar DTOs y listas blancas explícitas.
- Nunca aceptar roles o permisos desde el cliente.
- Auditar cambios de rol y separar la actualización de perfil de la administrativa.
- Probar con campos extra en cada endpoint de escritura.

## Referencias

- <https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html>
- <https://cwe.mitre.org/data/definitions/915.html>
- <https://portswigger.net/web-security/access-control>
