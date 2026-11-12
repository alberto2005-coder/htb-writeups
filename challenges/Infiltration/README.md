---
challenge: Infiltration
type: OSINT
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [osint, linkedin, instagram, dorks, social-media]
---

# Infiltration — Hack The Box (Challenge)

[🌍 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El objetivo es entrar en “Evil Corp LLC”. Buscando la empresa en LinkedIn se llega a su perfil y a un empleado; su Instagram contiene una foto con una etiqueta/nota visible. Ampliando la imagen se lee la flag.

## Enunciado y superficie

- OSINT, Easy, retirado.
- No hay binario ni servicio.
- Solo se da el nombre de la empresa y el objetivo.

## Reconocimiento

Se busca la empresa en un motor de búsqueda y en LinkedIn:

```text
"Evil Corp LLC" site:linkedin.com
```

El perfil de la empresa muestra una publicación con una cadena que parece base64. Al decodificarla se obtiene un mensaje de ánimo, no la flag.

## Análisis

Se identifican empleados y perfiles públicos. Uno de ellos tiene Instagram abierto. Se revisan las publicaciones y se buscan imágenes con texto, pizarras, badges o notas.

```bash
# Descargar la imagen y revisar metadatos/zoom
exiftool photo.jpg
```

La flag está en una etiqueta visible al ampliar una de las fotos.

## Explicación del fallo

La empresa y sus empleados publican información sensible en redes sociales: nombres, ubicaciones, badges y notas. La OSINT pasiva permite reconstruir el acceso sin tocar sistemas.

## Reproducción local

1. Buscar la empresa en LinkedIn.
2. Enumerar empleados y perfiles públicos.
3. Revisar Instagram y publicaciones con imágenes.
4. Ampliar la imagen y leer la etiqueta.

## Evidencia

- Captura del perfil de empresa con la cadena base64.
- Publicación de Instagram con la zona relevante recortada.
- Flag redactada.

## Lecciones aprendidas

- LinkedIn es una fuente clave de orgánica y empleados.
- Las fotos pueden filtrar badges, notas y ubicaciones.
- La OSINT pasiva no requiere interactuar con la víctima.
- Una cadena base64 puede ser una pista, no el secreto.

## Mitigación y detección

- Políticas de redes sociales y revisión de publicaciones.
- Difuminar badges y notas en fotos corporativas.
- Limitar la visibilidad de empleados y sedes.
- Formación sobre ingeniería social.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/osint/infiltration/>
- <https://osintframework.com/>
- <https://attack.mitre.org/techniques/T1593/001/>
