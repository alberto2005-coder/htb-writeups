---
machine: Secret
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, command-injection, suid, crash-dump, file-descriptors, privesc]
---

# Secret — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El repositorio Git del sitio expone el código; del análisis sale el secreto con el que se firman los JWT. Con un token de administrador se accede a funciones internas, una de ellas con command injection, y se obtiene shell como `dasith`. En `/opt` hay un SUID `count` con el código fuente y un `valgrind.log`; se abusa de dos formas: leer archivos a través de los descriptores abiertos del proceso o provocar un crash y leer el contenido desde el core dump.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `80`: nginx 1.18.0, sitio principal.
- `3000`: Node.js Express, API.

```bash
echo '<IP> secret.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://secret.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

El sitio principal es una landing con documentación. El repositorio `.git` está expuesto y se descarga con `git-dumper` o a mano. El código muestra:

- La generación y verificación de JWT.
- El secreto usado para firmar.
- Rutas de administración y una llamada a `exec` con entrada del usuario.
- La API en el puerto `3000`.

## Foothold

Con el secreto se firma un JWT con rol de administrador y se accede a las rutas internas. Una de ellas recibe un parámetro que se pasa a un comando del sistema; un separador ejecuta una reverse shell como `dasith`.

```bash
python3 -c "import jwt; print(jwt.encode({'role':'admin'}, '<SECRET>', algorithm='HS256'))"
```

## Movimiento lateral

No hay otro host. `dasith` no tiene `sudo`. En `/opt` aparecen tres archivos:

- `count`: binario SUID de root que cuenta caracteres, palabras y líneas.
- `code.c`: código fuente del binario.
- `valgrind.log`: salida de una ejecución con Valgrind.

## Escalada de privilegios

`count` abre el archivo indicado y guarda un resumen, pero no cierra el descriptor. Con `/proc/<PID>/fd/<N>` se puede acceder a un archivo legible situado en un directorio sin permiso de traversal, como `/root/.profile`; un archivo solo-root como `root.txt` sigue protegido por sus permisos.

La segunda ruta es provocar un crash: el binario habilita el core dump con `prctl(PR_SET_DUMPABLE, 1)`, y el volcado contiene el archivo que se leyó como root. Si el core se genera en una ruta accesible y con permisos laxos, se lee el contenido privilegiado desde el volcado.

```bash
/opt/count
# introducir /root/root.txt y provocar el fallo
ls -l /var/crash/
cat /var/crash/_opt_count.*.crash
```

## Evidencia

- `.git` expuesto y secreto JWT en el código.
- Token de administrador aceptado por la API.
- Command injection y `id` como `dasith`.
- `find / -perm -4000` con `/opt/count`.
- Código fuente y `valgrind.log`.
- Lectura por descriptor o core dump y `id` con UID 0.

## Lecciones aprendidas

- Un repositorio `.git` expuesto filtra código y secretos.
- Firmar JWT con un secreto estático permite forjar cualquier rol.
- Un binario SUID que abre archivos privilegiados puede filtrarlos por descriptores.
- Los core dumps de procesos privilegiados pueden contener información sensible.
- La combinación de SUID, `prctl` y volcados es una vía de elevación.

## Mitigaciones y detección

- No publicar `.git` ni secretos en el repositorio; usar variables de entorno.
- Rotar el secreto JWT y validar `iss`, `aud` y expiración.
- Evitar `exec` con entrada del usuario; usar APIs y listas de permitidos.
- Retirar SUID innecesarios y revisar los que abren archivos.
- Deshabilitar core dumps para procesos privilegiados o restringir su ruta.
- Alertar de descargas de `.git`, tokens de administrador y crashes en `/opt`.

## Referencias

- [0xdf — Secret](https://0xdf.gitlab.io/2022/03/26/htb-secret.html)
- [IppSec — Secret](https://www.youtube.com/watch?v=byYZl9CSFtM)
- [Hack The Box — Secret](https://app.hackthebox.com/machines/secret)
- [Knowledge — SUID: descriptores y crash dumps](../../../knowledge/linux/suid-fd-crashdump.md)
