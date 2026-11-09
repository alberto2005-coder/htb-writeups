---
challenge: Phonebook
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, ldap, ldap-injection, auth-bypass]
---

# Phonebook — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Una agenda de contactos con login. El formulario no monta una consulta SQL sino un filtro **LDAP**, y los comodines se cuelan sin escapar. `*` como usuario y como contraseña autentica, y el buscador devuelve todos los registros del directorio: entre ellos, el contacto que guarda la flag en su descripción.

## Enunciado

Aplicación Flask con dos pantallas: `/` (login) y `/home` (buscador de contactos por nombre).

## Análisis

El código filtra con algo equivalente a:

```python
filtro = "(&(cn=%s)(password=%s))" % (usuario, password)
con.search_s("dc=phonebook,dc=htb", ldap.SCOPE_SUBTREE, filtro)
```

Dos consecuencias:

1. Cualquier valor entra en el filtro, así que `*` actúa como comodín LDAP.
2. Al devolver el primer resultado, un filtro que case con varios usuarios devuelve el primero del árbol.

## Explotación

```text
usuario:  *
password: *
```

`(&(cn=*)(password=*))` casa con cualquier entrada que tenga ambos atributos: sesión iniciada. En `/home`, el buscador sufre lo mismo:

```text
búsqueda: *
```

Devuelve todos los contactos. En el listado aparece el usuario `admin` (o el que tenga permisos) con la flag en el campo `description`:

```text
HTB{<flag>}
```

Encadenado, un filtro más preciso sirve para enumerar atributos:

```text
*)(description=*
```

## Tropiezos

- **Comillas y paréntesis**: si la app escapa `(`, `)` y `\`, `*` sigue funcionando porque no es un metacaracter de escape LDAP.
- **Búsqueda vacía**: enviar cadena vacía devuelve el formulario otra vez; hay que enviar `*`.
- **Login con `admin*`**: si el bind es por `cn`, `admin*` también entra y es más sigiloso que `*`.

## Lecciones

- LDAP no es SQL, pero la inyección es idéntica en concepto: entrada sin escapar dentro de un filtro.
- Un comodín en el campo de contraseña convierte la autenticación en "existe el usuario".
- Mitigación: `ldap.filter.escape_filter_chars()` en cada valor, bind con la cuenta del usuario y comparación de contraseña fuera del filtro.
