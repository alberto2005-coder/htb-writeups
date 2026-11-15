---
topic: Xdebug — DBGp expuesto y ejecución PHP
tags: [linux, php, xdebug, dbgp, rce]
---

# Xdebug — DBGp expuesto y ejecución PHP

[🌐 English](xdebug-dbgp-rce.en.md) | **Español**

## Concepto

Xdebug en modo remoto acepta conexiones DBGp y permite evaluar expresiones PHP. Si el puerto 9000 es accesible y la cookie `XDEBUG_SESSION` activa la depuración, un cliente puede ejecutar `system()` como el usuario del servidor web.

## Cuándo aplica

- La cabecera `Xdebug` o `phpinfo` revela la extensión.
- El puerto 9000 es accesible desde el atacante.
- `xdebug.remote_connect_back` o un host fijo permiten la conexión.

## Procedimiento

1. Confirmar la versión y el modo remoto.
2. Escuchar en 9000 y enviar `XDEBUG_SESSION=1`.
3. Implementar el handshake DBGp y enviar `eval`.
4. Ejecutar `system()` y obtener una shell.

## Comandos

```bash
curl -H 'Cookie: XDEBUG_SESSION=1' http://<HOST>/index.php
python3 xdebug_client.py  # eval: system('id')
nc -lvnp 9000
```

## Variantes

- Usar el plugin de navegador para activar la sesión.
- `xdebug.remote_host` fijo y puerto alternativo.
- Evaluar `file_get_contents` para lectura.

## Limitaciones

- Xdebug puede estar en modo `develop` sin conexión.
- Un firewall bloquea 9000.
- La versión moderna usa `xdebug.mode=debug` y `client_host`.

## Mitigación

- Deshabilitar Xdebug en producción.
- Bloquear 9000 y no usar `remote_connect_back`.
- Separar el usuario web y revisar `php.ini`.

## Detección

- Conexiones salientes al puerto 9000.
- Peticiones con `XDEBUG_SESSION`.
- `system`, `exec` o `shell_exec` desde PHP-FPM.

## Referencias

- [Xdebug — remote debugging](https://xdebug.org/docs/remote)
- [0xdf — Olympus](https://0xdf.gitlab.io/2018/09/22/htb-olympus.html)
- [HackTricks — Xdebug](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/php-tricks-esp/index.html)
