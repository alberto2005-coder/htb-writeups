---
topic: PHP — inyección de filtros y cadenas de conversión
tags: [web, php, lfi, php-filter, file-read, rce]
---

# PHP — inyección de filtros y cadenas de conversión

[🇬🇧 English](php-filter-injection.en.md) | **Español**

## Concepto

Un LFI que permite `php://filter` puede convertir la lectura de un archivo en una escritura de código. Las cadenas de conversión (`convert.iconv`, `convert.base64-decode`) transforman datos controlados en una secuencia PHP válida que se incluye y ejecuta.

## Cuándo aplica

- Un parámetro llega a `include`, `require` o `file_get_contents`.
- El esquema `php://` no está bloqueado.
- El atacante controla parte del contenido leído (por ejemplo, un archivo subido o una sesión).

## Procedimiento

1. Confirmar el LFI y que `php://filter` funciona.
2. Construir una cadena con `php_filter_chain_generator`.
3. Escribir un webshell o ejecutar código en la respuesta.
4. Si hay `php-fpm`, combinar con una sesión envenenada.

```bash
python3 php_filter_chain_generator.py --chain '<?php system($_GET["c"]); ?>'
```

## Variantes

- `convert.base64-decode` para limpiar caracteres.
- Cadenas largas para evadir límites de longitud.
- Envenenar una sesión y usarla como fuente.

## Limitaciones

- `allow_url_include` debe estar activo para algunos flujos.
- La cadena puede superar el límite de la URL.
- Un `open_basedir` restringe los archivos accesibles.

## Mitigación

- No permitir `php://` en parámetros de include.
- Usar listas blancas de archivos y rutas absolutas.
- Deshabilitar `allow_url_include` y aislar sesiones.

## Detección

- Parámetros con `php://filter` o `convert.iconv`.
- URLs anormalmente largas.
- Includes de archivos en `uploads/` o sesiones.

## Referencias

- [Synacktiv — PHP filter chains](https://www.synacktiv.com/publications/php-filter-chains-file-read-from-error-based-oracle)
- [0xdf — Pollution](https://0xdf.gitlab.io/2023/07/01/htb-pollution.html)
- [PHP — wrappers](https://www.php.net/manual/en/wrappers.php.php)
