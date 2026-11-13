---
topic: Docker image layers
tags: [forensics, docker, containers, layers, supply-chain]
---

# Docker image layers

[🌐 English](docker-image-layers.en.md) | **Español**

## Concepto

Una imagen Docker es una pila de capas inmutables. Cada instrucción del Dockerfile añade una capa, y `docker image save` conserva todas ellas en un TAR con `manifest.json`, `repositories` y un `layer.tar` por capa. Borrar un archivo en una capa posterior no elimina el contenido de las anteriores.

## Cuándo aplica

- Investigación de imágenes públicas o de un registro comprometido.
- Búsqueda de secretos eliminados en una capa posterior.
- Análisis de una imagen antes de desplegarla.
- Retos con un TAR de imagen o un historial sospechoso.

## Requisitos y condiciones

- Imagen local o TAR exportado.
- Herramientas para listar y extraer TAR.
- Entorno aislado; no ejecutar binarios desconocidos.
- Conocimiento de `.wh.` y `.wh..wh..opq`.

## Procedimiento

1. Exportar la imagen con `docker image save`.
2. Listar el contenido del TAR y el manifiesto.
3. Revisar `docker history --no-trunc`.
4. Extraer cada `layer.tar` y comparar rutas.
5. Analizar archivos eliminados o marcados como opacos.
6. Verificar hashes y cadenas antes de abrir binarios.

```bash
docker image save <IMAGE> -o image.tar
7z l image.tar
docker history --no-trunc <IMAGE>
tar xvf <LAYER>/layer.tar
```

## Variantes

- Imágenes multi-stage con capas descartadas.
- Registros que conservan manifests antiguos.
- Capas base con secretos o binarios inesperados.
- Imágenes firmadas y verificadas con Cosign.

## Limitaciones

- La capa final no muestra lo que se borró.
- Los archivos `.wh.` no contienen el contenido eliminado.
- La procedencia de una imagen pública no garantiza seguridad.
- El análisis de binarios requiere un entorno controlado.

## Mitigación

- Firmar y verificar imágenes.
- Escanear todas las capas, no solo el resultado final.
- No incluir secretos en ninguna capa.
- Usar bases mínimas y reproducibles.
- Revisar el historial antes de desplegar.

## Detección

- Alertar de imágenes con capas que borran directorios sensibles.
- Comparar el historial con el Dockerfile esperado.
- Buscar `LD_PRELOAD`, binarios en `/usr/share` y archivos opacos.
- Monitorizar pulls de imágenes no firmadas.

## Referencias

- <https://docs.docker.com/build/cache/>
- <https://docs.docker.com/reference/cli/docker/image/save/>
- <https://attack.mitre.org/techniques/T1543/006/>
