---
title: WordPress — webshell escondido en un tema
tags: [web, wordpress, php, webshell, theme, persistence]
---

# WordPress — webshell escondido en un tema

[🇬🇧 English](wordpress-theme-webshell.en.md) | **Español**

## Concepto

Un tema de WordPress puede contener un archivo PHP malicioso que solo responde a un parámetro concreto. Al estar dentro de `wp-content/themes`, el servidor lo ejecuta y el tráfico se camufla entre assets legítimos. Es una persistencia habitual tras un compromiso.

## Cuándo aplica

- El tema activo tiene archivos que no coinciden con el oficial.
- `wpscan` enumera el tema y sus versiones.
- Hay un parámetro extraño en las peticiones o en el código ofuscado.

## Procedimiento

1. Enumerar temas y comparar con el repositorio oficial.
2. Buscar `eval`, `base64_decode`, `gzinflate` y variables `$_REQUEST`.
3. Desofuscar el archivo y localizar el parámetro y la clave.
4. Invocar el webshell con el parámetro correcto.

```bash
wpscan --url http://<IP> --enumerate t,tt
curl 'http://<IP>/wp-content/themes/<THEME>/<FILE>.php?<PARAM>=id'
```

## Variantes

- El webshell puede estar en `functions.php` con un hook `init`.
- Un plugin o un mu-plugin también sirve de persistencia.
- La clave puede estar en una cookie o en un header.

## Limitaciones

- El archivo debe ser accesible por HTTP.
- El parámetro y la clave deben descubrirse por análisis.
- Los WAF pueden bloquear la ejecución de comandos.

## Mitigación y detección

- Verificar la integridad con `wp core verify-checksums` y comparar temas.
- Auditar archivos nuevos y fechas de modificación.
- Aplicar el principio de mínimo privilegio al usuario web.
- Monitorizar peticiones a PHP de temas con parámetros de sistema.

## Referencias

- <https://developer.wordpress.org/themes/basics/theme-functions/>
- <https://wpscan.com/>
- <https://wordpress.org/documentation/article/hardening-wordpress/>
