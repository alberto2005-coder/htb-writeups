---
challenge: Monstrosity
type: OSINT
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [osint, twitter, geolocation, social-media, api]
---

# Monstrosity — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Se investiga un perfil de Twitter/X y sus publicaciones para geolocalizar una fotografía. La clave está en cruzar el texto, los metadatos y el entorno visual con herramientas de mapas.

## Enunciado y superficie

- OSINT, Medium, retirado.
- Se proporciona un usuario/perfil y una imagen o pista.
- No hay archivos de explotación ni instancia.

## Reconocimiento

1. Se archiva el perfil y se listan publicaciones, seguidores y fechas.
2. Se extraen metadatos de las imágenes (EXIF, software, GPS).
3. Se buscan referencias a ciudades, eventos o negocios.
4. Se usan búsquedas inversas de imagen y mapas.

```bash
exiftool image.jpg
```

## Análisis

- Se identifican puntos de referencia: arquitectura, señalización, vegetación, idioma.
- Se acota el país/ciudad por el texto y el horizonte.
- Se compara con Google Maps/Street View y con imágenes satelitales.
- Se confirma la ubicación con varias fuentes independientes.
- La flag se obtiene de la ubicación o de un objeto visible.

> **Limitación:** la API antigua de Twitter ya no está disponible; el flujo se documenta con archivos y capturas.

## Explicación del fallo

La combinación de un perfil público, imágenes sin limpiar metadatos y texto geográfico permite localizar a una persona o un lugar sin acceso técnico.

## Reproducción local

1. Guardar capturas del perfil.
2. Revisar EXIF y metadatos.
3. Hacer búsqueda inversa.
4. Contrastar con mapas.
5. Redactar la conclusión y la flag.

## Evidencia

- Capturas del perfil y publicaciones.
- Salida de `exiftool`.
- Comparación con mapas.
- Flag redactada.

## Lecciones aprendidas

- El texto y las imágenes se complementan.
- Los metadatos pueden eliminar la necesidad de geolocalizar.
- La confirmación requiere varias fuentes.
- Las APIs cambian; hay que archivar.

## Mitigación y detección

- Eliminar EXIF antes de publicar.
- Revisar el fondo de las fotos.
- Limitar la visibilidad del perfil.
- No publicar ubicaciones en tiempo real.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/osint/monstrosity/>
- <https://exiftool.org/>
- <https://www.google.com/maps/>
