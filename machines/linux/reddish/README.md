---
machine: Reddish
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, docker, node-red, redis, pivoting, rsync]
---

# Reddish — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Node-RED en 1880 permite crear un flujo con un nodo `exec` y obtener shell en su contenedor. Desde ahí se atraviesan tres redes Docker: Redis sin autenticación escribe un webshell, un cron con comodín entrega el usuario de `www` y un contenedor `backup` privilegiado monta el disco del host. Un cron en el host cierra con root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
1880/tcp  http  Node.js Express / Node-RED
172.19.0.2:6379  redis
172.19.0.4:80    http
172.20.0.2:873   rsync
```

## Enumeración

- `POST /` en 1880 devuelve un identificador y la ruta `/red/{id}` del editor.
- El editor permite arrastrar nodos `exec`, `http request` y `function` sin autenticación.
- El contenedor no tiene `curl`, `wget` ni `nc`; se usa Perl o un flujo de subida.
- Los escaneos internos revelan las redes `172.19.0.0/16` y `172.20.0.0/16`.

## Foothold

Se crea un flujo con un nodo `exec` que ejecuta una reverse shell Perl. El flujo se despliega y el callback llega como root del contenedor `nodered`. Como no hay conectividad directa al host, se levantan túneles con `socat` o Meterpreter para alcanzar los servicios internos.

```text
POST http://<IP>:1880/  ->  {"path":"/red/<ID>"}
```

## Movimiento lateral

Redis en `172.19.0.2:6379` no tiene `AUTH`. Se cambia `dir` y `dbfilename`, se escribe un webshell PHP y se guarda con `SAVE`; el sitio en `172.19.0.4` lo ejecuta. El webshell permite lanzar una shell como `www-data`.

En `www-data` se descubre un cron que ejecuta `rsync` con un comodín sobre un directorio escribible. Los nombres de archivo se interpretan como opciones de `rsync`; se crean archivos `-e` y un script para ejecutar comandos como el usuario del cron.

```bash
redis-cli -h 172.19.0.2
config set dir /var/www/html/<APP_DIR>
config set dbfilename shell.php
save
```

## Escalada de privilegios

El contenedor `backup` es accesible por `rsync` y corre con `--privileged`. Se escribe un cron dentro del contenedor para obtener root en `backup`; después se monta `/dev/sda1` y se accede al sistema de archivos del host.

Con `/etc/cron.d` del host montado y escribible, se deja un cron que ejecuta un script de root.

```bash
mount /dev/sda1 /mnt
echo '* * * * * root sh /opt/shell.sh' > /mnt/etc/cron.d/shell
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un editor de flujos sin autenticación es ejecución remota directa.
- Redis sin `AUTH` puede escribir archivos si el proceso tiene permisos.
- Los comodines de `rsync` y `tar` convierten nombres de archivo en opciones.
- `--privileged` da acceso a dispositivos del host y rompe el aislamiento.

## Mitigaciones y detección

- Autenticar Node-RED y limitar sus nodos peligrosos.
- Exigir `AUTH`, bind a loopback y permisos mínimos en Redis.
- Evitar comodines con directorios escribibles y usar `--` para terminarlos.
- No ejecutar contenedores privilegiados ni montar el disco del host.

## Referencias

- [0xdf — Reddish](https://0xdf.gitlab.io/2019/01/26/htb-reddish.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+reddish)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+reddish+writeup)
