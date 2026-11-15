---
topic: Inyección en eval de Python
tags: [linux, python, eval, sudo, privesc]
---

# Inyección en eval de Python

**English** | [🇪🇸 Español](python-eval-injection.md)

## Concept

A privileged script passes user-controlled data to `eval` or `exec`. Even without an explicit shell, the expression runs inside the process and can import modules and execute commands.

## When it applies

- Scripts run with `sudo` that process tickets, JSON, templates or formulas.
- Functions using `eval`, `exec`, `compile` or `pickle.loads` on external input.
- Applications that let users edit an expression and validate it only with blacklists.

## Procedure

1. Review `sudo -l` and read the privileged script.
2. Locate the `eval`/`exec` call and the controllable field.
3. Test a harmless expression that returns a calculation.
4. Import `os` and run the desired command.

```bash
sudo -l
sudo /usr/bin/python3 /opt/app/internals.py
# In the evaluated field:
__import__("os").system("id")
__import__("os").system("/bin/bash")
```

## Variants

- `exec` with multiple lines.
- `eval` inside a Jinja template or rule engine.
- `pickle`/`yaml.load` as equivalent deserialization.
- Filters blocking `os` but allowing `__import__`, `builtins` or `getattr`.

## Limitations

- The process must accept the expression without strict validation.
- Some environments restrict `__builtins__` or use a real sandbox.
- The expression must be syntactically valid for the parser.

## Mitigation and detection

- Never use `eval`/`exec` on external data; use `ast.literal_eval` or a data parser.
- Run privileged scripts with a dedicated account and no shell.
- Audit `sudo`, command lines and child processes.

## References

- <https://docs.python.org/3/library/functions.html#eval>
- <https://attack.mitre.org/techniques/T1059/006/>
- <https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Deserialization_Cheat_Sheet.html>
