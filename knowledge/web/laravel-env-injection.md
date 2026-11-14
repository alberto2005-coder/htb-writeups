---
topic: Laravel — inyección de entorno (CVE-2024-52301)
tags: [web, laravel, php, cve-2024-52301, auth-bypass]
---

# Laravel — inyección de entorno (CVE-2024-52301)

[🌐 English](laravel-env-injection.en.md) | **Español**

## Concepto

Cuando `register_argc_argv` está activo, Laravel puede interpretar parámetros de la query string como argumentos de consola. Un atacante cambia `APP_ENV` con un parámetro como `--env=preprod`; si la configuración de ese entorno omite autenticación o activa debug, se abre una ruta interna que no debería ser pública.

## Cuándo aplica

- La aplicación es Laravel y `register_argc_argv=On` en PHP.
- Existen entornos alternativos (`local`, `staging`, `preprod`) con controles distintos.
- La web muestra debug o un panel con bypass de login por entorno.

## Procedimiento

1. Fingerprint de Laravel y comprobar `APP_DEBUG` en respuestas de error.
2. Probar `?--env=local`, `?--env=staging` y variantes con `--env=preprod`.
3. Comparar el comportamiento: login omitido, rutas nuevas o debug expuesto.
4. Encadenar el acceso con la siguiente vulnerabilidad del panel.

## Comandos

```bash
curl -s "http://<HOST>/?--env=preprod" | head
curl -s "http://<HOST>/?--env=local" | grep -i "whoops\|debug\|login"
curl -s -o /dev/null -w "%{http_code}\n" "http://<HOST>/dashboard?--env=preprod"
```

## Variantes

- Añadir el parámetro a una ruta concreta en lugar de la raíz.
- Combinar `--env` con `--debug` si el framework lo acepta.
- Usar el cambio de entorno para alterar la base de datos o el almacenamiento de sesiones.

## Limitaciones

- Requiere `register_argc_argv=On`; muchos despliegues lo desactivan.
- No es RCE por sí solo: cambia la configuración de la aplicación.
- El entorno debe existir y tener un archivo `.env.<entorno>` válido.

## Mitigación

- Desactivar `register_argc_argv` y actualizar Laravel.
- No mantener entornos de desarrollo accesibles desde producción.
- Fijar `APP_ENV` en el servidor y revisar la configuración por entorno.

## Detección

- Peticiones con `--env=`, `--debug` o argumentos CLI en la query string.
- Cambios de comportamiento de login asociados a un parámetro.
- Errores de Laravel con trazas o variables de entorno expuestas.

## Referencias

- [0xdf — Environment](https://0xdf.gitlab.io/2025/09/06/htb-environment.html)
- [NVD — CVE-2024-52301](https://nvd.nist.gov/vuln/detail/CVE-2024-52301)
- [Laravel — Configuration](https://laravel.com/docs/11.x/configuration)
