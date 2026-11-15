---
topic: Subida Flask con ruta absoluta
tags: [web, flask, upload, path-join, rce]
---

# Subida Flask con ruta absoluta

[🌐 English](flask-absolute-path-upload.en.md) | **Español**

## Concepto

`os.path.join` descarta los componentes anteriores cuando uno posterior es absoluto. Si una aplicación valida `../` pero pasa el nombre de archivo a `os.path.join`, un nombre como `/app/app/views.py` escribe fuera del directorio de subidas.

## Cuándo aplica

- La aplicación permite subir archivos.
- El nombre se pasa a `os.path.join`.
- El código de la aplicación es escribible o se recarga.

## Procedimiento

1. Descargar el código fuente si está disponible.
2. Identificar una vista o archivo que se cargue al iniciar.
3. Subir un archivo con nombre absoluto.
4. Invocar la ruta para ejecutar el código.

```python
import os
os.path.join('/app', 'public', 'uploads', '/app/app/views.py')
# '/app/app/views.py'
```

```http
POST /upcloud HTTP/1.1
Content-Disposition: form-data; name="file"; filename="/app/app/views.py"
```

## Variantes

- Sobrescribir una plantilla o un archivo de configuración.
- Usar un nombre con barra inicial y extensión permitida.
- Combinar con Flask debug para ejecutar código.

## Limitaciones

- El proceso debe poder escribir el destino.
- El archivo debe cargarse o recargarse.
- La ruta absoluta debe ser aceptada.

## Mitigación y detección

- Usar `secure_filename` y confinar la ruta.
- Rechazar nombres absolutos y normalizar.
- Montar el código como solo lectura.

## Referencias

- <https://docs.python.org/3/library/os.path.html#os.path.join>
- <https://flask.palletsprojects.com/en/stable/patterns/fileuploads/>
- <https://attack.mitre.org/techniques/T1190/>
