---
topic: File upload
tags: [web, file-upload, webshell, mime, magic-bytes, bypass]
---

# File upload

[🌐 English](file-upload.en.md) | **Español**

## Concepto

Una subida insegura permite guardar un archivo ejecutable o leerlo desde una ruta controlada. Las defensas suelen basarse en extensión, tipo MIME o contenido; cada una puede fallar por separado si el servidor confía en el cliente o no normaliza el nombre.

## Cuándo aplica

- Formularios de avatar, documento o importación.
- Filtros de extensión o MIME.
- Directorio de subidas servido por el webroot.
- Procesamiento posterior con una biblioteca vulnerable.

## Procedimiento

1. Identificar extensión, MIME y tamaño permitidos.
2. Probar variantes de extensión y mayúsculas.
3. Manipular `Content-Type` y magic bytes.
4. Comprobar si el archivo se sirve o se ejecuta.
5. Buscar una ruta de ejecución o de lectura.

```bash
curl -F 'file=@sh.php;type=image/png' http://<HOST>/upload
curl -F 'file=@sh.phtml' http://<HOST>/upload
curl -F 'file=@shell.jpg' http://<HOST>/upload
```

## Variantes

- Bypass con `.php5`, `.phtml`, `.phar` o doble extensión.
- Polyglot con cabecera de imagen y código PHP.
- `.htaccess` para interpretar otra extensión.
- Path traversal en el nombre del archivo.

## Limitaciones

- El directorio debe ser accesible o ejecutable.
- El servidor puede renombrar el archivo.
- La validación puede usar magic bytes.
- El antivirus puede eliminar el payload.

## Mitigación y detección

- Validar contenido real y extensión permitida.
- Generar nombres aleatorios y almacenar fuera del webroot.
- Deshabilitar ejecución en el directorio de subidas.
- Alertar de extensiones ejecutables y archivos con cabeceras mixtas.

## Referencias

- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://portswigger.net/web-security/file-upload>
