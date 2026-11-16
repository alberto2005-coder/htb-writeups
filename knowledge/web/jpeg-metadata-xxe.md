---
topic: JPEG — metadatos controlados y XXE en el proceso
tags: [web, xxe, jpeg, exiftool, metadata, file-read]
---

# JPEG — metadatos controlados y XXE en el proceso

[🌐 English](jpeg-metadata-xxe.en.md) | **Español**

## Concepto

Una aplicación lee el campo `Artist` de un JPEG y lo usa para construir la ruta de un XML de créditos. Si el atacante controla la imagen y el log que apunta a ella, puede dirigir la ruta a un XML propio. Ese XML declara una entidad externa que lee un archivo del servidor; el proceso, que corre como root, escribe el contenido en la respuesta.

## Cuándo aplica

- La aplicación procesa metadatos de imágenes subidas o accesibles.
- El valor del metadato se concatena en una ruta de archivo.
- El XML resultante se parsea con entidades externas habilitadas.
- El proceso tiene privilegios altos.

## Procedimiento

1. Identificar el campo de metadatos usado en la ruta.
2. Crear un JPEG con `exiftool -Artist=...` apuntando al XML.
3. Crear el XML con `<!ENTITY xxe SYSTEM "file:///...">`.
4. Hacer que la aplicación procese la imagen (subida, log o cron).
5. Leer el resultado donde la aplicación guarde el campo.

## Comandos

```bash
exiftool -Artist="../tmp/x" x.jpg
```

```xml
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///root/.ssh/id_rsa">]>
<credits><image><root>&xxe;</root></image></credits>
```

## Variantes

- Usar `exiftool` con `-Comment` o `-ImageDescription`.
- Apuntar a `/etc/passwd` para confirmar la lectura.
- Encadenar con un log escribible para controlar la ruta.
- Leer claves SSH y usarlas para entrar.

## Limitaciones

- El parser debe resolver entidades externas.
- La ruta construida debe ser accesible por el proceso.
- El archivo debe procesarse después de la subida.
- El resultado debe poder leerse.

## Mitigación

- Deshabilitar entidades externas (`resolve_entities=False`).
- No construir rutas con metadatos de usuario.
- Validar el `Artist` contra una lista blanca.
- Ejecutar el procesamiento con un usuario sin privilegios.

## Detección

- JPEG con `Artist` que contiene `../` o rutas absolutas.
- XML con `DOCTYPE` y `ENTITY SYSTEM`.
- Lecturas de claves SSH por procesos de imagen.
- Errores de parser al procesar créditos.

## Referencias

- [OWASP — XXE](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)
- [ExifTool — Documentación](https://exiftool.org/)
- [0xdf — RedPanda](https://0xdf.gitlab.io/2022/11/26/htb-redpanda.html)
