---
topic: Moodle — RCE mediante plugin malicioso
tags: [web, moodle, plugin, rce, xss]
---

# Moodle — RCE mediante plugin malicioso

[🌐 English](moodle-plugin-rce.en.md) | **Español**

## Concepto

Moodle permite a un administrador instalar plugins desde un ZIP. Si se consigue una sesión de administrador —por ejemplo con una XSS almacenada que roba la cookie—, se puede subir un plugin `local` con código PHP y ejecutarlo desde una ruta accesible.

## Cuándo aplica

- Moodle antiguo con autoinscripción o perfiles editables.
- Plugins de terceros sin revisión y `dataroot` accesible.
- XSS almacenada en mensajes, badges o nombres de curso.

## Procedimiento

1. Identificar la versión y el tema con `/lib/upgrade.txt` o los assets.
2. Conseguir una sesión de administrador mediante XSS o credenciales reutilizadas.
3. Crear un plugin `local` mínimo con `version.php` y una página PHP.
4. Subirlo desde `Administración del sitio > Plugins > Instalar plugins`.
5. Ejecutar la página del plugin y obtener una shell.

## Comandos

```bash
# Empaquetar un plugin local mínimo
zip -r moodle-rce.zip moodle-rce
# Subida autenticada (requiere sesión de admin y sesskey)
curl -s -b cookies.txt -F 'repo_upload_file=@moodle-rce.zip' \
  'http://<HOST>/admin/tool/installaddon/index.php?sesskey=<SESSKEY>'
```

## Variantes

- XSS en el perfil para robar `MoodleSession`.
- Instalación de un tema o filtro en lugar de un plugin `local`.
- Uso de un plugin legítimo vulnerable para ejecutar PHP.

## Limitaciones

- Se necesita una cuenta con capacidad de instalar plugins.
- El ZIP debe respetar la estructura `moodle-rce/version.php`.
- La instalación puede requerir confirmación y permisos de escritura.

## Mitigación

- Mantener Moodle y los plugins actualizados.
- Restringir la instalación de plugins a administradores de confianza.
- Aplicar CSP y escapar la salida para reducir el robo de sesión.

## Detección

- Plugins nuevos o modificados fuera de una ventana de mantenimiento.
- Peticiones a `admin/tool/installaddon` y escrituras en `dataroot`.

## Referencias

- <https://moodle.org/security/>
- <https://community.owasp.org/attacks/xss/>
