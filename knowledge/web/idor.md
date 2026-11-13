---
topic: IDOR
tags: [web, api, idor, authorization, access-control, burp]
---

# IDOR

[🌐 English](idor.en.md) | **Español**

## Concepto

Insecure Direct Object Reference ocurre cuando una API acepta un identificador de objeto y no comprueba que el usuario autenticado tenga permiso sobre él. Cambiar un número, UUID o nombre de recurso puede revelar datos de otra cuenta o permitir acciones administrativas.

## Cuándo aplica

- Endpoints con `id`, `user_id`, `account` o UUID.
- Paneles con objetos compartidos.
- APIs que confían en el identificador del cliente.
- Operaciones de lectura, edición o borrado.

## Procedimiento

1. Crear dos cuentas con permisos distintos.
2. Capturar una petición autenticada.
3. Cambiar el identificador por el de la otra cuenta.
4. Comparar código, longitud y contenido.
5. Probar también métodos y campos ocultos.

```bash
curl -s -H 'Authorization: Bearer <TOKEN_A>' https://<HOST>/api/users/1001
curl -s -H 'Authorization: Bearer <TOKEN_A>' https://<HOST>/api/users/1002
```

## Variantes

- IDOR horizontal entre usuarios del mismo rol.
- IDOR vertical hacia funciones de administrador.
- Mass assignment de `role` o `owner`.
- Enumeración de UUID y objetos borrados.

## Limitaciones

- El servidor debe usar el identificador sin comprobar propiedad.
- Los UUID aleatorios dificultan la enumeración.
- Algunas respuestas ocultan datos pero permiten acciones.
- Rate limiting puede bloquear pruebas masivas.

## Mitigación y detección

- Autorizar por objeto en el servidor, no por ocultar IDs.
- Usar identificadores opacos y comprobar pertenencia.
- Aplicar listas de campos permitidos.
- Alertar de accesos a objetos de otras cuentas y cambios de rol.

## Referencias

- <https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control>
- <https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html>
- <https://portswigger.net/web-security/access-control/idor>
