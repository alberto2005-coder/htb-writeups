---
sherlock: Fragility
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, exfiltration, archive, metadata, encoding]
---

# Fragility — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Se analiza un archivo exfiltrado que contiene un mensaje oculto. La combinación de metadatos, compresión y codificación permite reconstruir la secuencia y el contenido.

## Escenario

Una organización detecta la salida de un archivo sospechoso. Se entrega una copia y se pide determinar qué contiene, cómo se ocultó y qué usuario lo preparó.

## Artefactos

- Archivo comprimido o documento.
- Metadatos y nombres de entrada.
- Cadenas, hashes y posible esteganografía.

## Metodología

1. Se calcula el hash y se identifica el tipo real con `file`/`binwalk`.
2. Se listan entradas y fechas del archivo sin extraerlo.
3. Se revisan metadatos y comentarios.
4. Se prueban capas de compresión/codificación (base64, gzip, ZIP anidado).
5. Se documenta el mensaje y la relación con el usuario.

```bash
file evidence.bin
binwalk evidence.bin
7z l evidence.zip
exiftool evidence.docx
```

## Preguntas tipo

- ¿Qué tipo real de archivo es?
- ¿Cuántas capas de compresión tiene?
- ¿Qué usuario o ruta aparece en los metadatos?
- ¿Qué mensaje queda tras decodificar?
- ¿Cuándo se creó/modificó?

## Herramientas

`file`, `binwalk`, `7-Zip`, `ExifTool`, `CyberChef`.

## Evidencia y redacción

Se conservan hashes, listados y capturas del mensaje con usuarios y rutas redactados.

## Lecciones aprendidas

- La extensión no determina el tipo real.
- Los archivos anidados ocultan contenido simple.
- Los metadatos pueden atribuir la preparación.
- Documentar capas evita perder el orden.

## Detección

- Alertar de compresión y salida de datos sensibles.
- Revisar adjuntos con doble extensión.
- Correlacionar con accesos a unidades de red.
- Aplicar DLP en correo y endpoints.

## Referencias

- <https://app.hackthebox.com/sherlocks/Fragility>
- <https://attack.mitre.org/techniques/T1560/001/>
- <https://attack.mitre.org/techniques/T1027/>
