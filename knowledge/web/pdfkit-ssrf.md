---
topic: SSRF y lectura de archivos con PDFKit
tags: [web, ruby, pdfkit, ssrf, file-read, cve-2022-25765]
---

# SSRF y lectura de archivos con PDFKit

[🇬🇧 English](pdfkit-ssrf.en.md) | **Español**

## Concepto

PDFKit convierte HTML o una URL en PDF usando `wkhtmltopdf`. Si la URL la elige el usuario y no se restringe, el servidor puede solicitar recursos internos o leer archivos con `file://`. Versiones antiguas permiten además inyectar opciones.

## Cuándo aplica

- Formularios que generan PDF desde una URL.
- `PDFKit.new(params[:url])` sin lista de hosts.
- Metadatos que revelan `pdfkit`/`wkhtmltopdf`.

## Procedimiento

1. Generar un PDF con una URL propia y revisar metadatos.
2. Probar `http://127.0.0.1` y puertos internos.
3. Probar `file:///etc/passwd`.
4. Revisar la versión y las opciones aceptadas.
5. Confirmar el impacto sin publicar datos sensibles.

```bash
curl -s 'http://<IP>/' --data-urlencode 'url=file:///etc/passwd'
```

## Variantes

- Inyección de opciones en `wkhtmltopdf`.
- SSRF a metadatos cloud (`169.254.169.254`).
- Lectura de claves y configuración.

## Limitaciones

- Una lista de hosts y esquemas bloquea el ataque.
- El servicio puede ejecutarse sin red.
- Los permisos del proceso limitan la lectura.

## Mitigación

- Permitir solo `https` y hosts conocidos.
- Bloquear IPs privadas y metadatos.
- Actualizar PDFKit y no concatenar opciones.
- Ejecutar el conversor en un sandbox sin secretos.

## Detección

- Peticiones a `127.0.0.1`, `file://` y `169.254.169.254`.
- PDFs generados desde hosts internos.
- Errores de `wkhtmltopdf`.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2022-25765>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://attack.mitre.org/techniques/T1190/>
