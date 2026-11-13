---
topic: Python path join upload
tags: [linux, python, flask, upload, path-traversal, secure-filename]
---

# Python path join upload

[🌐 English](python-path-join-upload.en.md) | **Español**

## Concepto

`os.path.join(base, user_value)` descarta `base` cuando `user_value` es absoluto. Si una aplicación Flask o Django usa el nombre de archivo enviado por el cliente sin `secure_filename`, el atacante puede escribir en cualquier ruta permitida por el proceso, no solo dentro del directorio de subidas.

## Cuándo aplica

- Formularios de subida de XML, imágenes, CSV o documentos.
- Aplicaciones que guardan el archivo antes de validarlo.
- Errores que revelan la ruta guardada.
- Directorios de scripts o cron escribibles por el servicio web.

## Requisitos y condiciones

- Control del campo `filename` del multipart.
- Permiso de escritura del proceso web en la ruta destino.
- Conocimiento de una ruta útil, como un directorio de scripts.
- Ausencia de canonicalización o de comprobación de prefijo.

## Procedimiento

1. Identificar el parámetro de subida y el directorio base.
2. Enviar un `filename` con ruta absoluta.
3. Confirmar la escritura por el error, por la respuesta o por una descarga.
4. Buscar un consumidor de esa ruta: cron, importación, plantilla o tarea.
5. Ejecutar el código en el siguiente ciclo del consumidor.

```python
files = {
    "xml_file": ("/var/www/app/scripts/task.py", open("payload.py", "rb")),
    "xslt_file": ("stub.xslt", open("stub.xslt", "rb")),
}
requests.post("http://<HOST>/convert", files=files, cookies=cookies)
```

## Variantes

- `filename` absoluto.
- Secuencias `../` si el framework no las normaliza.
- Enlaces simbólicos en el directorio de subidas.
- Escritura en un directorio incluido en `PYTHONPATH`.

## Limitaciones

- El proceso debe poder escribir en el destino.
- Algunos frameworks normalizan o rechazan rutas absolutas.
- La ruta puede estar fuera del alcance del servidor web.
- El archivo debe ser consumido por un proceso útil.

## Mitigación

- Usar `werkzeug.utils.secure_filename`.
- Resolver la ruta y comprobar que empieza por el directorio permitido.
- Guardar con un nombre generado y extensión validada.
- No ejecutar scripts desde directorios escribibles por el servicio web.

## Detección

- Alertar de nombres de archivo con `/`, `..` o rutas absolutas.
- Monitorizar escrituras en directorios de scripts.
- Revisar errores de parseo que mencionan rutas inesperadas.
- Auditar cron y procesos que importan archivos de directorios de subida.

## Referencias

- <https://docs.python.org/3/library/os.path.html#os.path.join>
- <https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.utils.secure_filename>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://attack.mitre.org/techniques/T1059/006/>
