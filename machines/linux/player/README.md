---
machine: Player
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, ffmpeg, lshell, privesc]
---

# Player — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Los vhosts revelan una web con JWT HS256; una copia de seguridad expone la clave de firma y permite forjar un `access_code` de administrador. El panel usa ffmpeg para procesar AVI y el demuxer refleja el contenido de archivos locales. Se obtienen credenciales de `telegen`, se escapa de lshell con `su -s /bin/bash` y se llega a Codiad, donde un cron de root incluye un archivo escribible o deserializa `merge.log`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` Apache con varios vhosts.
- `ffuf -H 'Host: FUZZ.player.htb'` encuentra `staging`, `chat`, `admin` y `api`.
- El vhost principal usa una API con JWT.

## Enumeración

- `/backup/` contiene un archivo con la clave `secret` del JWT HS256.
- El token incluye `access_code`; al forjarlo con el rol `admin` se accede al panel.
- El panel permite subir archivos multimedia y llama a `ffmpeg` para generar miniaturas.

## Foothold

Con la clave se firma un JWT con `access_code` de administrador. En el panel, un AVI manipulado hace que el demuxer de ffmpeg lea un archivo local y lo muestre en el error o en la miniatura; así se lee `/etc/passwd` y la configuración de la aplicación.

```bash
python3 jwt_tool.py <TOKEN> -S hs256 -p '<SECRET>' -I -pc access_code -pv admin
```

## Movimiento lateral

La lectura de archivos revela credenciales de `telegen`. Su shell es lshell, que restringe comandos; `su -s /bin/bash telegen` abre una bash normal sin pedir contraseña. En su home hay acceso a Codiad.

```bash
su -s /bin/bash telegen
```

## Escalada de privilegios

Codiad tiene un webshell en `components/filemanager/controller.php`. Un cron de root ejecuta `buff.php`, que incluye un archivo escribible o deserializa `merge.log`; se coloca el payload y se espera la ejecución.

```bash
echo '<?php system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash"); ?>' > /var/www/html/codiad/merge.log
```

## Evidencia

- Clave JWT en `/backup/` y token de administrador forjado.
- AVI con lectura de archivos locales por ffmpeg.
- Credenciales de `telegen` y escape de lshell.
- `merge.log` interpretado por el cron de root.

## Lecciones aprendidas

- Una clave JWT filtrada invalida toda la autenticación.
- ffmpeg procesa entradas no confiables y puede filtrar archivos.
- Una shell restringida no equivale a una cuenta sin privilegios.

## Mitigación y detección

- Rotar la clave JWT y no guardar copias en el webroot.
- Ejecutar ffmpeg en un sandbox sin acceso al sistema de archivos.
- Revisar crons que incluyen o deserializan archivos del webroot.

## Referencias

- [0xdf — Player](https://0xdf.gitlab.io/2020/01/18/htb-player.html)
- [IppSec — Player](https://www.youtube.com/watch?v=JpzREo7XLOY)
- [Hack The Box — Player](https://app.hackthebox.com/machines/player)
