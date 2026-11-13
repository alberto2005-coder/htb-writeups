---
challenge: Peel Back The Layers
type: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, docker, image-layers, shared-library, elf]
---

# Peel Back The Layers — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una imagen Docker pública fue modificada para incluir una biblioteca compartida maliciosa y después se borró en una capa posterior. El historial de capas conserva el archivo y `LD_PRELOAD` explica su ejecución. La flag está embebida en la biblioteca.

## Enunciado y superficie

- Forensics, Medium, retirado.
- La imagen es `steammaintainer/gearrepairimage`.
- Se pide recuperar el backdoor insertado y eliminado.

```bash
docker pull steammaintainer/gearrepairimage:latest
docker image save steammaintainer/gearrepairimage -o image.tar
```

## Reconocimiento

- `image.tar` contiene `manifest.json`, `repositories` y capas.
- Solo algunas capas tienen contenido; las demás son metadatos.
- El historial muestra `rm -rf /usr/share/lib/` en una capa posterior.

```bash
7z l image.tar
cat manifest.json
```

## Análisis

1. Localizar la capa que copia archivos a `/usr/share/lib`.
2. Extraer su `layer.tar`.
3. Revisar el archivo `.wh..wh..opq`, que indica un directorio opaco.
4. Extraer `librs.so`.
5. Analizar la biblioteca con `file`, `strings` y Ghidra.

```bash
7z l <LAYER>/layer.tar
tar xvf <LAYER>/layer.tar
file usr/share/lib/librs.so
```

## Explicación del fallo

El atacante abusó del historial de una imagen pública para distribuir un backdoor y después intentó ocultarlo eliminando el directorio. Docker conserva las capas antiguas: borrar un archivo en una capa nueva no lo elimina de las anteriores.

La variable `LD_PRELOAD` apuntaba a `librs.so`, por lo que el cargador dinámico ejecutaba la biblioteca antes que las demás.

## Reproducción local

- Cargar la imagen o el TAR en un entorno aislado.
- Inspeccionar el historial con `docker history --no-trunc`.
- Extraer capas y comparar rutas.
- Analizar `librs.so` sin ejecutarla.

```bash
docker history --no-trunc steammaintainer/gearrepairimage:latest
strings -a usr/share/lib/librs.so | grep -Ei 'HTB|http|connect|LD_PRELOAD'
```

## Evidencia

- Capas y tamaños.
- Ruta `usr/share/lib/librs.so`.
- Constantes o cadenas que forman la flag, redactadas.
- Configuración de `LD_PRELOAD`.

## Lecciones aprendidas

- Las capas de Docker son inmutables y acumulativas.
- Borrar en una capa posterior no elimina el contenido anterior.
- Una biblioteca compartida puede ejecutarse en cada proceso que herede `LD_PRELOAD`.

## Mitigaciones y detección

- Firmar imágenes y verificar su procedencia.
- Escanear todas las capas, no solo el sistema de archivos final.
- Restringir `LD_PRELOAD` y variables de entorno en contenedores.
- Auditar imágenes públicas antes de desplegarlas.

## Referencias

- <https://www.hackthebox.com/challenges/Peel%20Back%20The%20Layers>
- <https://docs.docker.com/build/cache/>
- <https://attack.mitre.org/techniques/T1543/006/>
