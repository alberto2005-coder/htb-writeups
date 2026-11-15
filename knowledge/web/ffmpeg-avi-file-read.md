---
topic: ffmpeg — lectura de archivos locales con AVI
tags: [web, ffmpeg, file-read, media, cve]
---

# ffmpeg — lectura de archivos locales con AVI

[🇬🇧 English](ffmpeg-avi-file-read.en.md) | **Español**

## Concepto

ffmpeg procesa contenedores y códecs muy diversos. Un AVI manipulado puede hacer que el demuxer lea una ruta local y la incluya en un mensaje de error, en los metadatos o en un fotograma. Si la aplicación convierte o genera miniaturas de archivos subidos, la lectura de archivos queda expuesta.

## Cuándo aplica

- El panel acepta vídeo y llama a ffmpeg para transcodificar o crear thumbnails.
- La salida de error o el resultado se devuelve al usuario.
- ffmpeg corre con acceso a rutas sensibles.

## Procedimiento

1. Identificar la versión y el comando que ejecuta ffmpeg.
2. Crear un AVI con un chunk que apunte a `/etc/passwd` o a una clave.
3. Subirlo y solicitar la miniatura o la conversión.
4. Leer el contenido en la respuesta o en el error.

```bash
ffmpeg -f lavfi -i color=c=black:s=32x32 -t 1 -c:v rawvideo -f avi base.avi
# modificar el chunk de texto o el nombre de archivo y subir el resultado
```

## Variantes

- Listas de concatenación con `file 'http://...'` o rutas locales.
- `-vf subtitles=` con un archivo local.
- Metadatos que se copian al archivo de salida.

## Limitaciones

- La ruta debe ser accesible por el usuario de ffmpeg.
- La aplicación debe mostrar el error o el resultado.
- Un sandbox con `open_basedir` o contenedor sin secretos reduce el impacto.

## Mitigación

- Ejecutar ffmpeg en un contenedor sin secretos y sin red.
- Validar el tipo real del archivo y limitar códecs.
- No devolver errores internos al usuario.

## Detección

- Procesos ffmpeg con rutas fuera del directorio de trabajo.
- Avisos de demuxer sobre archivos que no son multimedia.
- Picos de CPU por conversiones de archivos pequeños.

## Referencias

- [ffmpeg — security](https://ffmpeg.org/security.html)
- [0xdf — Player](https://0xdf.gitlab.io/2020/01/18/htb-player.html)
- [CWE-200 — Exposure of Sensitive Information](https://cwe.mitre.org/data/definitions/200.html)
