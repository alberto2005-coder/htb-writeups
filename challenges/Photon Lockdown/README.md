---
challenge: Photon Lockdown
category: Challenge
type: Hardware
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [hardware, firmware, squashfs, rootfs, iot, credentials]
---

# Photon Lockdown — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Firmware de un ONT doméstico: dos ficheros de versión y una imagen `rootfs` en SquashFS. Al extraerla aparece la configuración por defecto con la contraseña de superusuario en claro; esa contraseña es la flag. No hay binario que revertir: el fallo es dejar credenciales de fábrica dentro del firmware.

## Enunciado y superficie

- Categoría **Hardware**, dificultad **Very Easy**.
- Entrega `fwu_ver`, `hw_ver` y `rootfs`.
- El objetivo es obtener acceso al dispositivo a partir del firmware.

```bash
file fwu_ver hw_ver rootfs
cat fwu_ver hw_ver
```

```text
fwu_ver: 3.0.5
hw_ver:  X1
rootfs:  Squashfs filesystem, little endian, version 4.0, zlib
```

## Reconocimiento

```bash
binwalk rootfs
unsquashfs -l rootfs | head -30
```

`binwalk` confirma que no hay capas ocultas: es un SquashFS directo. El listado muestra una jerarquía Linux compacta con `/etc`, `/bin` y `/www`.

## Análisis del código

```bash
unsquashfs rootfs
grep -ril "password\|passwd\|admin" squashfs-root/etc | head
```

El interés está en `etc/config_default.xml`, el fichero que el dispositivo copia a su configuración en el primer arranque. Contiene el usuario y la contraseña del panel:

```xml
<Value Name="SUSER_PASSWORD" Value="<HTB{...}>"/>
```

## Explicación del fallo

El firmware incluye la contraseña de fábrica en texto plano dentro de la imagen, y esa contraseña es única para el modelo. Cualquiera con el firmware puede extraerla y entrar en todos los dispositivos que no la hayan cambiado.

```bash
grep -r "SUSER_PASSWORD" squashfs-root/etc/
```

## Reproducción local

```bash
unsquashfs rootfs -d rootfs_out
grep -r "SUSER_PASSWORD" rootfs_out/etc/
# alternativa sin extraer:
strings rootfs | grep -i "SUSER_PASSWORD"
```

## Explotación

1. Extraer el SquashFS.
2. Leer `config_default.xml` y localizar `SUSER_PASSWORD`.
3. Usar esa credencial en el panel del dispositivo (o entregarla como flag, según el reto).

No hace falta emular el firmware ni conectar hardware.

## Evidencia

- `file` de `rootfs` confirmando SquashFS.
- `grep` con la línea de `SUSER_PASSWORD` y el valor recortado.

## Lecciones aprendidas

- El firmware es un sistema de ficheros: si se puede descargar, se puede leer.
- Las credenciales de fábrica compartidas por modelo son una puerta abierta en toda la flota.
- `unsquashfs` y `strings` resuelven la mayoría de estos retos sin `binwalk -e`.
- La versión del firmware (`fwu_ver`) sirve para buscar CVEs del modelo, aunque aquí no haga falta.

## Mitigaciones y detección

- Generar una contraseña única por dispositivo en el primer arranque y forzar su cambio.
- No incluir credenciales en texto plano en la imagen; usar un secreto por unidad o un provisioning seguro.
- Firmar el firmware y verificar la actualización.
- Detección: accesos al panel con la credencial por defecto y dispositivos que nunca han cambiado la contraseña.
- Referencias: OWASP IoT Top 10 (I1 credenciales débiles), MITRE T1078.001.

## Referencias

- <https://www.hackthebox.com/challenges/photon-lockdown>
- <https://0x42697262.github.io/birbrain/writeups/HackTheBox/photon_lockdown.html>
- <https://dua2z3rr.github.io/posts/Photon-Lockdown-Writeup>
- <https://github.com/plougher/squashfs-tools>
