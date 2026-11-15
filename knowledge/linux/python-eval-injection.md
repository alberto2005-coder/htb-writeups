---
topic: Inyección en eval de Python
tags: [linux, python, eval, sudo, privesc]
---

# Inyección en eval de Python

[🌐 English](python-eval-injection.en.md) | **Español**

## Concepto

Un script privilegiado pasa datos controlados por el usuario a `eval` o `exec`. Aunque el script no exponga una shell, la expresión se evalúa en el proceso y puede importar módulos y ejecutar comandos.

## Cuándo aplica

- Scripts ejecutados con `sudo` que procesan tickets, JSON, plantillas o fórmulas.
- Funciones que usan `eval`, `exec`, `compile` o `pickle.loads` sobre entrada externa.
- Aplicaciones que permiten editar una expresión y la validan solo con listas negras.

## Procedimiento

1. Revisar `sudo -l` y leer el script privilegiado.
2. Localizar la llamada a `eval`/`exec` y el campo controlable.
3. Probar una expresión inocua que devuelva un cálculo.
4. Importar `os` y ejecutar el comando deseado.

```bash
sudo -l
sudo /usr/bin/python3 /opt/app/internals.py
# En el campo evaluado:
__import__("os").system("id")
__import__("os").system("/bin/bash")
```

## Variantes

- `exec` con varias líneas.
- `eval` dentro de una plantilla Jinja o un motor de reglas.
- `pickle`/`yaml.load` como deserialización equivalente.
- Filtros que bloquean `os` pero permiten `__import__`, `builtins` o `getattr`.

## Limitaciones

- El proceso debe aceptar la expresión sin validación estricta.
- Algunos entornos restringen `__builtins__` o usan un sandbox real.
- La expresión debe ser sintácticamente válida para el parser.

## Mitigación y detección

- No usar `eval`/`exec` con datos externos; usar `ast.literal_eval` o un parser de datos.
- Ejecutar scripts privilegiados con una cuenta dedicada y sin shell.
- Auditar `sudo`, líneas de comandos y procesos hijos.

## Referencias

- <https://docs.python.org/3/library/functions.html#eval>
- <https://attack.mitre.org/techniques/T1059/006/>
- <https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Deserialization_Cheat_Sheet.html>
