---
challenge: Locked Away
category: Misc
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, pyjail, python, blacklist, exec]
---

# Locked Away — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

PyJail de manual: el programa comprueba una lista negra de cadenas y pasa lo que sobrevive a `exec()`. La lista incluye `open`, `flag`, `read`, `eval`, `exec`, `import`, corchetes y comillas, pero **no** incluye `clear`. Con `blacklist.clear()` la lista queda vacía y la siguiente orden puede llamar a `open_chest()` sin restricciones.

## Enunciado y superficie

- Categoría Misc, dificultad Easy; Business CTF 2024.
- Se entrega `main.py` y una instancia remota por `nc`.
- El enunciado plantea una prueba de acceso: hay que abrir el cofre.

## Reconocimiento

```bash
nc <IP> <PUERTO>
```

El servicio muestra un banner ASCII y el prompt `The chest lies waiting... `. Cada orden se valida contra la lista negra; si contiene alguna subcadena prohibida responde `Invalid command!` y vuelve a preguntar. Si la orden lanza una excepción, el programa imprime `You have been locked away...` y termina: no hay extracción booleana.

## Análisis del código

```python
blacklist = [
    'import', 'os', 'sys', 'breakpoint',
    'flag', 'txt', 'read', 'eval', 'exec',
    'dir', 'print', 'subprocess', '[', ']',
    'echo', 'cat', '>', '<', '"', "'", 'open'
]

while True:
    command = input('The chest lies waiting... ')
    if any(b in command for b in blacklist):
        print('Invalid command!')
        continue
    try:
        exec(command)
    except Exception:
        print('You have been locked away...')
        exit(1337)
```

La comprobación es una búsqueda de subcadenas, no un análisis sintáctico: cualquier orden que no contenga literalmente esos términos pasa. `open_chest()` es la función que lee `flag.txt` y lo imprime, pero contiene `open` y `flag`, así que no se puede escribir directamente.

## Explicación del fallo

La lista negra protege el nombre de la función, no el objeto. `blacklist` es una lista global normal y `exec` corre en el mismo espacio de nombres, así que la propia lista es un objeto manipulable. Vaciar la lista no requiere escribir `[]` ni comillas: el método `clear()` no aparece en ninguna entrada prohibida.

## Reproducción local

```bash
python3 main.py
```

En local, crear un `flag.txt` de prueba permite comprobar la cadena completa sin tocar la instancia remota.

## Explotación

```text
The chest lies waiting... blacklist.clear()
The chest lies waiting... open_chest()
```

1. `blacklist.clear()` pasa el filtro porque no contiene ninguna subcadena de la lista (ni corchetes, ni comillas, ni `open`).
2. La lista queda vacía; a partir de ahí `any(...)` siempre es falso.
3. `open_chest()` ya se puede llamar tal cual y devuelve el contenido del fichero.

Variantes equivalentes: reasignar con `blacklist.__init__()` o construir la llamada con `getattr(__builtins__...)`, pero `clear()` es la más corta y la que documenta el autor.

## Evidencia

- `Invalid command!` al enviar `open_chest()` sin vaciar la lista.
- Banner y prompt del servicio.
- Contenido del cofre guardado en `private/`.

## Lecciones aprendidas

- **Filtrar nombres no es aislar**: mientras el intérprete siga siendo el mismo, el atacante puede modificar el propio filtro.
- **Los métodos evitan los corchetes**: `clear()` no necesita `[]` ni comillas, justo lo que bloqueaba la lista.
- **Una excepción cierra la puerta**: conviene probar primero en local; un error de sintaxis en remoto termina el proceso.

## Mitigaciones y detección

- No se ejecuta entrada del usuario con `exec`/`eval`: no existe lista negra fiable.
- Si hace falta un intérprete restringido, usar un subproceso sin privilegios, sin ficheros sensibles y con `seccomp`/contenedor; nunca el mismo proceso.
- Detección: servicios que llaman a `exec` sobre `input()` y comparan contra una lista de cadenas; en logs, órdenes con `clear()`, `__builtins__` o `getattr` son señal de jailbreak.

## Referencias

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BEasy%5D%20Locked%20Away>
- <https://blog.ikuamike.io/posts/2024/htb_business_ctf_2024_misc>
- <https://docs.python.org/3/library/functions.html#exec>
