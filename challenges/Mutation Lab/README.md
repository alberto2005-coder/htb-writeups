---
challenge: Mutation Lab
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, svg, file-read, session-forgery, flask]
---

# Mutation Lab — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La app procesa SVG subidos y permite leer archivos locales mediante referencias externas. Con el secreto de sesión filtrado se forja una cookie de administrador y se obtiene la flag.

## Enunciado y superficie

- Web, Easy, retirado.
- Subida/procesamiento de imágenes SVG.
- Sesión en cookie.

```bash
curl -i http://<HOST>/
```

## Reconocimiento

Se revisa el código y se confirma que el SVG se renderiza en el servidor. Se prueba una referencia a `file:///etc/passwd` o a una ruta interna.

```xml
<svg xmlns="http://www.w3.org/2000/svg">
  <image href="file:///etc/passwd"/>
</svg>
```

## Análisis

1. Se sube el SVG y se observa si el contenido se refleja.
2. Se lee el archivo de configuración de la app.
3. Se extrae `SECRET_KEY`.
4. Se forja una cookie de sesión con rol admin.
5. Se accede al panel y se lee la flag.

```python
from flask.sessions import SecureCookieSessionInterface
# firmar {'user':'admin'} con la SECRET_KEY filtrada
```

## Explicación del fallo

El renderizador SVG permite referencias externas y la clave de sesión está en un archivo legible. La app confía en una cookie firmada con un secreto filtrado.

## Reproducción local

1. Montar la app Flask.
2. Subir el SVG.
3. Leer la configuración.
4. Forjar la cookie.
5. Acceder al panel.

## Evidencia

- SVG malicioso.
- Archivo leído y secreto redactado.
- Cookie forjada y flag redactada.

## Lecciones aprendidas

- SVG puede referenciar recursos externos.
- Los secretos de sesión no deben ser legibles por la app.
- Una cookie firmada no es seguro si la clave se filtra.
- El renderizado de archivos de usuario es peligroso.

## Mitigación y detección

- Deshabilitar referencias externas en SVG.
- Rotar `SECRET_KEY` y usar un gestor de secretos.
- Validar y sanear SVG.
- Monitorizar accesos a archivos de configuración.

## Referencias

- <https://www.hackthebox.com/challenges/mutation-lab>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://flask.palletsprojects.com/en/stable/quickstart/#sessions>
