---
topic: mPDF — lectura de archivos desde plantillas
tags: [linux, mpdf, file-read, pdf, lfi]
---

# mPDF — lectura de archivos desde plantillas

[🌐 English](mpdf-file-read.en.md) | **Español**

## Concepto

mPDF genera PDF a partir de HTML y permite incluir recursos locales. Si una aplicación pasa una ruta controlada por el usuario a una plantilla, una imagen o un `@import`, la librería resuelve `file://` y rutas relativas. El resultado es lectura de archivos del servidor, incluida configuración con credenciales.

## Cuándo aplica

- La aplicación genera PDF con mPDF y acepta plantillas o rutas.
- El parámetro no se limita a un directorio.
- Se buscan credenciales o código fuente.

## Procedimiento

1. Identificar el endpoint de generación de PDF.
2. Probar rutas absolutas y `file://` en el parámetro.
3. Leer configuración, `.env` o claves SSH.
4. Reutilizar las credenciales en SSH u otro servicio.

## Comandos

```bash
curl -s "http://<HOST>/pdf.php?template=../../../../etc/passwd"
curl -s "http://<HOST>/pdf.php?template=file:///var/www/.env"
curl -s -o out.pdf "http://<HOST>/report?html=file:///etc/passwd"
```

## Variantes

- Inyectar `file://` en una etiqueta `img` o `link`.
- Usar `@import` de CSS para leer archivos.
- Encadenar con SSRF para alcanzar servicios internos.

## Limitaciones

- mPDF puede bloquear `file://` en versiones recientes.
- El archivo debe ser legible por el usuario del servicio.
- La salida puede estar en el PDF y requerir extracción.

## Mitigación

- Limitar plantillas a un directorio y permitir lista.
- Deshabilitar `file://` y recursos remotos.
- Ejecutar el generador con un usuario sin acceso a secretos.

## Detección

- Parámetros de plantilla con `../` o `file://`.
- PDFs que contienen `/etc/passwd` o `.env`.
- Lecturas de archivos desde el proceso PHP.

## Referencias

- [mPDF — Documentation](https://mpdf.github.io/)
- [0xdf — Faculty](https://0xdf.gitlab.io/2022/10/22/htb-faculty.html)
- [CWE-22 — Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
