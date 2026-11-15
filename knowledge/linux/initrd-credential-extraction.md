---
topic: initrd — extracción de credenciales de arranque
tags: [linux, initrd, cpio, credentials, privesc]
---

# initrd — extracción de credenciales de arranque

[🌐 English](initrd-credential-extraction.en.md) | **Español**

## Concepto

El initrd contiene scripts y binarios que se ejecutan antes del sistema real. Si es legible, se puede descomprimir y revisar `cryptroot`/`uinitrd`; a veces incluye la contraseña de root o un binario que la genera.

## Cuándo aplica

- El usuario pertenece a `grub` o puede leer `/boot`.
- El initrd no está cifrado ni firmado.
- Hay scripts de desbloqueo LUKS o `uinitrd`.

## Procedimiento

1. Localizar el initrd y comprobar el formato.
2. Descomprimir con `zcat` y `cpio`.
3. Revisar `scripts/local-top/cryptroot`.
4. Ejecutar el binario o leer la contraseña.

## Comandos

```bash
zcat /boot/initrd.img-<VER> | cpio -idm
./sbin/uinitrd <ARG>
su root
```

## Variantes

- Initrd con `cryptsetup` y clave embebida.
- Binario que deriva la clave de un argumento.
- Backup de `/boot` en otro host.

## Limitaciones

- El initrd puede estar firmado o cifrado.
- El binario puede requerir el host original.
- La contraseña puede estar rotada.

## Mitigación

- Restringir lectura de `/boot` y del grupo `grub`.
- Firmar/verificar initrd y usar TPM.
- No incluir secretos en scripts de arranque.

## Detección

- Lecturas de `/boot/initrd*` por usuarios no root.
- Ejecución de `uinitrd` fuera del arranque.
- Cambios en scripts de `cryptroot`.

## Referencias

- [0xdf — Unattended](https://0xdf.gitlab.io/2019/08/24/htb-unattended.html)
- [Linux — initrd](https://www.kernel.org/doc/html/latest/admin-guide/initrd.html)
- [cpio — manual](https://www.gnu.org/software/cpio/manual/)
