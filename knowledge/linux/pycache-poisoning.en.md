---
topic: Python — `__pycache__` poisoning
tags: [linux, python, pycache, bytecode, privesc]
---

# Python — `__pycache__` poisoning

**English** | [🌐 Español](pycache-poisoning.md)

## Concept

Python stores compiled bytecode in `__pycache__` and loads it when it matches the `.py` stamp. If a privileged script imports a module from a writable directory and the `.pyc` can be replaced, the interpreter runs the attacker bytecode even if the original `.py` is unchanged.

## When it applies

- A sudo script imports modules from a writable directory.
- `__pycache__` exists or can be created.
- The `.py` and `.pyc` are not protected by permissions.

## Procedure

1. Review `sudo -l` and the executed script.
2. Locate the import directory and `__pycache__`.
3. Compile a malicious `.pyc` with the expected name.
4. Run the script with sudo and verify the load.

## Commands

```bash
sudo -l
find / -type d -name __pycache__ -writable 2>/dev/null
python3 -c "import py_compile; py_compile.compile('payload.py', cfile='__pycache__/module.cpython-311.pyc')"
sudo /usr/bin/python3 /opt/app/script.py
```

## Variants

- Place a same-named `.py` if the directory allows it.
- Abuse `PYTHONPATH` or a `sitecustomize.py`.
- Poison the cache of a cron-run tool.

## Limitations

- The Python version must match the `.pyc`.
- The `.py` timestamp or hash must validate the cache.
- The directory may be read-only for the user.

## Mitigation

- Mount code and `__pycache__` read-only.
- Run with `PYTHONDONTWRITEBYTECODE=1`.
- Do not run scripts from writable directories with sudo.

## Detection

- New `.pyc` files in application directories.
- Privileged scripts importing from `/tmp` or home.
- Bytecode hashes differing from the expected ones.

## References

- [Python — bytecode caching](https://docs.python.org/3/reference/import.html#cached-bytecode)
- [0xdf — Browsed](https://0xdf.gitlab.io/2026/03/28/htb-browsed.html)
- [CWE-94 — Code Injection](https://cwe.mitre.org/data/definitions/94.html)
