---
topic: PHP — LFI con php://filter y zip://
tags: [web, php, lfi, php-filter, zip-wrapper, rce]
---

# PHP — LFI con php://filter y zip://

[🌐 English](php-filter-zip-wrapper.en.md) | **Español**

## Concepto

Un LFI que concatena `.php` puede leer código con `php://filter` y ejecutar un archivo subido con `zip://` o `phar://`. La combinación convierte una inclusión de archivos en divulgación de fuente y RCE.

## Cuándo aplica

- Un parámetro se usa en `include`/`require`.
- Se puede subir un ZIP o PHAR.
- Los wrappers no están deshabilitados.

## Procedimiento

1. Confirmar el LFI y el sufijo añadido.
2. Leer el código con `php://filter/convert.base64-encode`.
3. Subir un ZIP con un PHP.
4. Incluirlo con `zip://` y ejecutar un comando.

## Comandos

```bash
curl -s 'http://<HOST>/?op=php://filter/convert.base64-encode/resource=home' | base64 -d
curl -s 'http://<HOST>/?op=zip://uploads/<IP>/<FILE>.zip%23shell.php&cmd=id'
```

## Variantes

- `phar://` para deserialización.
- `data://` si `allow_url_include` está activo.
- `expect://` en instalaciones antiguas.

## Limitaciones

- `allow_url_include=Off` no bloquea `zip://`.
- El sufijo `.php` debe poder añadirse al nombre del ZIP.
- El directorio de uploads debe ser accesible por ruta relativa.

## Mitigación

- Lista blanca de archivos y rutas absolutas.
- Deshabilitar wrappers innecesarios.
- Guardar uploads fuera del webroot y renombrarlos.

## Detección

- Peticiones con `php://`, `zip://`, `phar://` o base64 en parámetros.
- Accesos a uploads seguidos de ejecución PHP.
- Errores de inclusión con rutas codificadas.

## Referencias

- [PHP — wrappers](https://www.php.net/manual/en/wrappers.php)
- [0xdf — CrimeStoppers](https://0xdf.gitlab.io/2018/06/03/htb-crimestoppers.html)
- [HackTricks — LFI](https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/index.html)
