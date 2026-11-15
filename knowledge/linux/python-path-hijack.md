---
title: PYTHONPATH — secuestrar un import privilegiado
tags: [linux, python, pythonpath, privesc, sudo]
---

# PYTHONPATH — secuestrar un import privilegiado

[🇬🇧 English](python-path-hijack.en.md) | **Español**

## Concepto

Cuando un script Python se ejecuta como root, `sys.path` incluye el directorio del script y las rutas de `PYTHONPATH`. Si el atacante puede escribir en alguna de ellas, un módulo con el mismo nombre que uno importado se carga en lugar del legítimo y se ejecuta como root.

## Cuándo aplica

- `sudo -l` muestra `python3 /ruta/script.py`.
- El directorio del script es escribible por el usuario.
- `sudo` conserva `PYTHONPATH` (`env_keep`) o el script importa un módulo ausente.

## Procedimiento

1. Leer el script y anotar sus `import`.
2. Comprobar permisos del directorio y de `PYTHONPATH`.
3. Crear un módulo con el nombre importado que ejecute una shell.
4. Ejecutar el script por sudo y confirmar `id`.

```bash
printf 'import os\nos.system("/bin/bash -p")\n' > /opt/app/subprocess.py
sudo /usr/bin/python3 /opt/app/app.py
```

## Variantes

- `sitecustomize.py` o `usercustomize.py` en una ruta de `sys.path`.
- Un `__init__.py` en un paquete que se importa desde el directorio actual.
- `PYTHONPATH=.` en un `sudo` mal configurado.

## Limitaciones

- El directorio debe ser escribible.
- `sudo` puede limpiar `PYTHONPATH` o usar `secure_path`.
- El módulo legítimo puede estar antes en `sys.path`.

## Mitigación y detección

- No ejecutar scripts en directorios escribibles como root.
- Limpiar `PYTHONPATH` y usar `-I`/`-P` en Python.
- Revisar `env_keep` en sudoers.
- Auditar imports y archivos `.py` nuevos junto a scripts privilegiados.

## Referencias

- <https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH>
- <https://docs.python.org/3/library/sys.html#sys.path>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html>
