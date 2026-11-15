---
topic: Python — envenenamiento de `__pycache__`
tags: [linux, python, pycache, bytecode, privesc]
---

# Python — envenenamiento de `__pycache__`

[🌐 English](pycache-poisoning.en.md) | **Español**

## Concepto

Python guarda el bytecode compilado en `__pycache__` y lo carga si coincide con la marca del `.py`. Si un script privilegiado importa un módulo desde un directorio escribible y el `.pyc` se puede reemplazar, el intérprete ejecuta el bytecode del atacante aunque el `.py` original no cambie.

## Cuándo aplica

- Un script con sudo importa módulos de un directorio escribible.
- `__pycache__` existe o se puede crear.
- El `.py` y su `.pyc` no están protegidos por permisos.

## Procedimiento

1. Revisar `sudo -l` y el script ejecutado.
2. Localizar el directorio de importación y `__pycache__`.
3. Compilar un `.pyc` malicioso con el nombre esperado.
4. Ejecutar el script con sudo y comprobar la carga.

## Comandos

```bash
sudo -l
find / -type d -name __pycache__ -writable 2>/dev/null
python3 -c "import py_compile; py_compile.compile('payload.py', cfile='__pycache__/module.cpython-311.pyc')"
sudo /usr/bin/python3 /opt/app/script.py
```

## Variantes

- Colocar un `.py` con el mismo nombre si el directorio lo permite.
- Aprovechar `PYTHONPATH` o un `sitecustomize.py`.
- Envenenar el caché de una herramienta que se ejecuta por cron.

## Limitaciones

- La versión de Python debe coincidir con el `.pyc`.
- La marca de tiempo o el hash del `.py` deben validar el caché.
- El directorio puede ser de solo lectura para el usuario.

## Mitigación

- Montar el código y `__pycache__` como solo lectura.
- Ejecutar `PYTHONDONTWRITEBYTECODE=1`.
- No ejecutar scripts de directorios escribibles con sudo.

## Detección

- `.pyc` nuevos en directorios de aplicación.
- Scripts privilegiados que importan desde `/tmp` o home.
- Hashes de bytecode distintos de los esperados.

## Referencias

- [Python — bytecode caching](https://docs.python.org/3/reference/import.html#cached-bytecode)
- [0xdf — Browsed](https://0xdf.gitlab.io/2026/03/28/htb-browsed.html)
- [CWE-94 — Code Injection](https://cwe.mitre.org/data/definitions/94.html)
