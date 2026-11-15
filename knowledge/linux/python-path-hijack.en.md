---
title: PYTHONPATH — hijacking a privileged import
tags: [linux, python, pythonpath, privesc, sudo]
---

# PYTHONPATH — hijacking a privileged import

[🇪🇸 Español](python-path-hijack.md) | **English**

## Concept

When a Python script runs as root, `sys.path` includes the script directory and the `PYTHONPATH` entries. If the attacker can write to one of them, a module with the same name as a legitimate import loads instead and runs as root.

## When it applies

- `sudo -l` shows `python3 /path/script.py`.
- The script directory is writable by the user.
- `sudo` preserves `PYTHONPATH` (`env_keep`) or the script imports a missing module.

## Procedure

1. Read the script and note its `import`s.
2. Check directory and `PYTHONPATH` permissions.
3. Create a module with the imported name that runs a shell.
4. Run the script through sudo and confirm `id`.

```bash
printf 'import os\nos.system("/bin/bash -p")\n' > /opt/app/subprocess.py
sudo /usr/bin/python3 /opt/app/app.py
```

## Variants

- `sitecustomize.py` or `usercustomize.py` on a `sys.path` entry.
- An `__init__.py` in a package imported from the current directory.
- `PYTHONPATH=.` in a misconfigured `sudo`.

## Limitations

- The directory must be writable.
- `sudo` may clear `PYTHONPATH` or use `secure_path`.
- The legitimate module may come earlier in `sys.path`.

## Mitigation and detection

- Do not run scripts from writable directories as root.
- Clear `PYTHONPATH` and use `-I`/`-P` in Python.
- Review `env_keep` in sudoers.
- Audit imports and new `.py` files next to privileged scripts.

## References

- <https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH>
- <https://docs.python.org/3/library/sys.html#sys.path>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html>
