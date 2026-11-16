---
machine: Resource
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, phar, deserialization, ssh-certificates, har, bash, glob, privesc]
---

# Resource — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El centro de tickets permite adjuntar un ZIP y acceder a un archivo mediante un filtro PHAR, lo que ejecuta una webshell incluida en el ZIP. La base de datos y un `.har` filtran credenciales de `msainristil`; su home contiene la CA SSH antigua todavía confiada, con la que se firma una clave para root en el contenedor ITRC. En el host principal, la API de firma y un script con sudo permiten obtener principals y, mediante una comparación Bash sin comillas, filtrar la clave privada de la CA de IT y firmar una clave `root_user`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,2222 <IP>
```

- `22` y `2222` SSH de hosts distintos, `80` nginx delante de Apache.
- Aplicación de tickets en `itrc.ssg.htb`.
- El panel permite crear tickets y adjuntar archivos; los adjuntos se guardan en `/uploads/<hash>.zip`.

## Enumeración

Se crea un ticket con un ZIP que contiene `shell.php`. La aplicación comprueba la existencia con una ruta controlada; al usar `phar://uploads/<hash>.zip/shell` se interpreta el archivo interno como PHP y se obtiene `www-data`. La base MariaDB contiene `tickets`, `messages` y `users`; un `.har` adjunto incluye credenciales de `msainristil`.

## Foothold

Las credenciales de `msainristil` funcionan en el contenedor por SSH (22) y por 2222. En `/etc/ssh` está `ca-it` y una CA antigua de ITRC; la clave privada de la CA antigua permite firmar una clave con principal `root_user` y entrar como root en el contenedor.

```bash
# PHAR en ticket
curl 'http://itrc.ssg.htb/ticket.php?id=<ID>&page=phar://uploads/<HASH>.zip/shell'
# firma local
sudo /opt/sign_key.sh /dev/shm/file /etc/passwd <USER> <PRINCIPAL> 1
# certificado root
ssh-keygen -s ca-it -z 223 -I <USER> -V -5m:forever -n root_user key.pub```

## Movimiento lateral

Como root del contenedor se lee `/home/zzinter/sign_key_api.sh`, que usa un token para llamar a `signserv.ssg.htb/v1/sign`. Se piden certificados con los principals `support` y `zzinter_temp` y se entra al host principal como `zzinter`.

## Escalada de privilegios

`zzinter` puede ejecutar `/opt/sign_key.sh` con sudo. El script compara `[[ $itca == $ca ]]` sin comillas; un archivo con wildcard hace que Bash expanda el patrón y la comparación tenga éxito solo si el prefijo coincide. Se fuerza carácter a carácter la clave privada de `ca-it`, se firma una clave con principal `root_user` y se entra como root en el host principal.

## Evidencia

- ZIP con webshell y filtro PHAR.
- `.har` con credenciales de `msainristil`.
- CA antigua confiada y root en ITRC.
- API de firma, principals y comparación Bash glob.

## Lecciones aprendidas

- Los filtros de archivos y PHAR pueden ejecutar código en archivos aparentemente inertes.
- Los `.har` capturan credenciales y tokens de sesión.
- Las CA SSH antiguas siguen siendo confiables si no se retiran.
- Una comparación Bash sin comillas permite globbing y fuga de secretos.

## Mitigación y detección

- No aceptar archivos comprimidos con PHP ni usar wrappers sobre uploads.
- Sanitizar `.har` y no adjuntar sesiones con credenciales.
- Retirar CAs antiguas y rotar sus claves.
- Citar variables en comparaciones Bash y usar `[[ ]]` correctamente.

## Referencias

- [0xdf — Resource](https://0xdf.gitlab.io/2024/11/23/htb-resource.html)
- [IppSec — Resource](https://www.youtube.com/watch?v=ZIzxodu8axg)
- [Hack The Box — Resource](https://app.hackthebox.com/machines/resource)
