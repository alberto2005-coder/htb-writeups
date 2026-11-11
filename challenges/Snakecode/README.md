---
challenge: Snakecode
category: Reversing
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, python, pyc, marshal, uncompyle6]
---

# Snakecode — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Se entrega `chall.pyc`, bytecode de **Python 2.7**. `uncompyle6` recupera un script que carga funciones desde blobs base64 + zlib + `marshal` y lanza un Snake en `curses`. La «manzana» (`$`) va cambiando de carácter y va escribiendo la flag sobre el tablero. No hay que jugar bien: se instrumenta `snake()` para registrar los parámetros o se hace trampa subiendo la puntuación y fijando la posición, y se leen los caracteres.

## Enunciado y superficie

- Categoría Reversing, dificultad Easy.
- Se entrega un único fichero, `chall.pyc`.
- El enunciado no da código fuente: solo el bytecode compilado.

## Reconocimiento

```bash
file chall.pyc
```

```text
chall.pyc: python 2.7 byte-compiled
```

Ejecutarlo abre una partida de Snake en la terminal. El binario no acepta argumentos ni red.

## Análisis del código

Se descompila en un contenedor con Python 2.7, porque `uncompyle6` necesita esa versión para bytecode 2.7:

```bash
docker run -v "$PWD":/ctf -it python:2.7 bash
pip install uncompyle6
uncompyle6 chall.pyc > chall.py
```

El resultado importa `marshal`, `types` y `time`, y construye funciones con:

```python
ll = types.FunctionType(marshal.loads(base64.b64decode(blob)), globals())
```

Los blobs están comprimidos con zlib; `marshal` reconstruye el código y `FunctionType` lo convierte en función. El `snake()` visible solo inicializa el estado y llama en bucle a `m2`:

```python
def snake(w):
    r = i0(); c = i1(); f0(w)
    d = (0, 1); p = [(5, 5)]; pl = 1; s = 0; l = None
    while 1:
        p, d, pl, l, s, w, c, r = m2(p, d, pl, l, s, w, c, r)
        time.sleep(0.4)
```

- `p` son las coordenadas del cuerpo de la serpiente.
- `pl` es la puntuación y crece al comer.
- `d` es la dirección; `s` el número de movimientos.
- La manzana cambia de carácter según avanza la partida y va componiendo la flag.

## Explicación del fallo

La flag no se compara en ningún momento: **se muestra**. El juego la revela de forma lenta y ligada al estado (comer manzanas), pero el estado está en memoria y se puede modificar. Es un caso de «secreto en el flujo de ejecución», no de criptografía.

## Reproducción local

Con el contenedor de Python 2.7 y `curses` disponible, `python chall.py` abre el tablero. La partida termina cuando la serpiente se enreda; por eso conviene instrumentar antes de jugar en serio.

## Explotación

**Opción A — registrar estado.** Añadir un log dentro de `snake()`:

```python
with open('log.txt', 'a') as fd:
    ...
    fd.write('p=%s; d=%s; pl=%s; l=%s; s=%s\n' % (p, d, pl, l, s))
```

Tras unos movimientos, `log.txt` muestra la posición de la manzana y la puntuación; los caracteres de la flag aparecen en la manzana.

**Opción B — hacer trampa.** Modificar el bucle para no perder y para que la manzana se renueve en cada paso:

```python
while 1:
    p, d, pl, l, s, w, c, r = m2(p, d, pl, l, s, w, c, r)
    pl += 1
    p = [(5, 5)]
    time.sleep(0.4)
```

Así la serpiente no muere, la puntuación sube y cada movimiento pinta el siguiente carácter. Anotando lo que sale en pantalla se reconstruye la flag, que se guarda en `private/`.

## Evidencia

- `chall.pyc`, bytecode de Python 2.7.
- Funciones reconstruidas con `marshal` + zlib desde base64.
- Flag visible en la manzana durante la partida; no se publica.

## Lecciones aprendidas

- **Versión de Python**: `uncompyle6` con bytecode 2.7 falla en Python 3; el contenedor `python:2.7` evita media hora de errores.
- **`marshal` no es cifrado**: solo serializa código; quien tiene el `.pyc` puede reconstruirlo.
- **Jugar no es el camino**: la partida está limitada por la longitud de la serpiente; instrumentar o hacer trampa es más rápido.

## Mitigaciones y detección

- Un `.pyc` distribuido no protege nada: `uncompyle6`, `decompyle3` o `pycdc` recuperan el código.
- Si hay que entregar bytecode, que no contenga secretos ni lógica de validación; la verificación va al servidor.
- Detección: ficheros `.pyc` con blobs base64 de alta entropía y llamadas a `marshal.loads` son señal de ofuscación.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/snakecode/>
- <https://github.com/rocky/python-uncompyle6>
- <https://docs.python.org/3/library/marshal.html>
