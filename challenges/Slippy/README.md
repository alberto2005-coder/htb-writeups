---
challenge: Slippy
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, tar, path-traversal, ssti, file-upload]
---

# Slippy — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La app extrae archivos TAR subidos sin validar las rutas. Un `../` escribe una plantilla fuera del directorio previsto y la SSTI resultante ejecuta comandos.

## Enunciado y superficie

- Web, Medium, retirado.
- Subida de archivos `.tar`.
- Renderizado de plantillas.

```bash
curl -i http://<HOST>/
```

## Reconocimiento

Se revisa el código y se confirma la extracción con `tarfile`/`tar`. Se inspeccionan las rutas internas y el directorio de plantillas.

## Análisis

1. Se crea un TAR con una entrada `../../templates/evil.html`.
2. Se sube y se extrae.
3. Se visita la plantilla para confirmar SSTI.
4. Se ejecuta un comando.
5. Se lee la flag.

```bash
tar -cvf evil.tar --transform 's|^|../../templates/|' evil.html
```

```text
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
```

## Explicación del fallo

La extracción no normaliza las rutas ni limita el destino. El archivo escapa del directorio y se interpreta como plantilla, lo que lleva a RCE.

## Reproducción local

1. Montar la app de subida/extracción.
2. Crear el TAR malicioso.
3. Subir y visitar.
4. Ejecutar `id`.
5. Validar rutas y comparar.

## Evidencia

- Listado del TAR.
- Ruta escrita.
- SSTI y flag redactada.

## Lecciones aprendidas

- Los TAR pueden contener `../`.
- La extracción debe validar rutas.
- Las plantillas editables son RCE.
- El sandbox de subida es imprescindible.

## Mitigación y detección

- Normalizar y validar rutas de extracción.
- Extraer en directorio aislado sin ejecución.
- No permitir plantillas de usuario.
- Monitorizar escrituras fuera del upload dir.

## Referencias

- <https://www.hackthebox.com/challenges/slippy>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://docs.python.org/3/library/tarfile.html#tarfile-extractall>
