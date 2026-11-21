---
topic: VirtualBox — VDI cifrado y LUKS
tags: [forense, virtualbox, vdi, luks, hashcat, credenciales, moderators]
---

# VirtualBox — VDI cifrado y LUKS

[🌐 English](virtualbox-vdi-luks.en.md) | **Español**

## Concepto

Una máquina virtual de VirtualBox se compone de un archivo `.vbox` con la configuración y un disco `.vdi`. VirtualBox puede cifrar el disco, y dentro del sistema invitado puede haber además una partición LUKS. Para acceder a los datos hay que romper o conocer las dos capas: la contraseña de cifrado de VirtualBox y la de LUKS. En Moderators, `2019.vdi` estaba protegido por ambas y la contraseña resultante servía para `sudo`.

## Cuándo aplica

- Hay un `.vdi` y un `.vbox` accesibles en un home, share o backup.
- El disco está cifrado por VirtualBox (`encryption` en el `.vbox`).
- Dentro hay LUKS u otro cifrado de disco.
- Las contraseñas son débiles o reutilizadas.

## Procedimiento

1. Copiar el `.vdi` y el `.vbox` al equipo de análisis.
2. Identificar el cifrado y extraer el material necesario.
3. Romper la contraseña de VirtualBox con `pyvboxdie-cracker` o con el hash que genera `virtualbox2hashcat.py`.
4. Descifrar el VDI y montarlo o convertirlo.
5. Detectar y abrir la partición LUKS.
6. Buscar credenciales y archivos de configuración.

## Comandos

```bash
file 2019.vdi
python3 pyvboxdie-cracker.py -v 2019-08-01.vbox -d /usr/share/wordlists/rockyou.txt
```

```bash
# Tras descifrar y montar el VDI
cryptsetup luksDump /dev/loopXpY
cryptsetup luksOpen /dev/loopXpY vdi_crypt
mount /dev/mapper/vdi_crypt /mnt
```

## Variantes

- `VBoxManage encryptmedium` con la contraseña conocida.
- Extracción del hash de VirtualBox con herramientas específicas.
- Uso de `qemu-nbd` para montar el VDI.
- Prueba local de la frase LUKS con `cryptsetup luksOpen --test-passphrase`; Hashcat no soporta LUKS2 en esa versión.
- Búsqueda de la contraseña en el `.vbox`, scripts o notas.

## Limitaciones

- Las contraseñas fuertes hacen inviable el crackeo.
- El cifrado de VirtualBox y LUKS son capas independientes.
- El VDI puede estar incompleto o dañado.
- Montar discos requiere permisos y herramientas.
- Los datos pueden estar en una instantánea o disco diferencial.

## Mitigación

- Usar contraseñas largas y únicas para VirtualBox y LUKS.
- No guardar VMs con credenciales en homes de usuarios.
- Cifrar backups y restringir su acceso.
- Rotar credenciales encontradas en imágenes.
- Auditar el acceso a archivos `.vdi` y `.vbox`.

## Detección

- Copias de `.vdi`/`.vbox` fuera del host.
- Ejecución de `pyvboxdie-cracker`, `hashcat` o `cryptsetup`.
- Montajes de imágenes de disco en equipos de usuario.
- Credenciales de la VM usadas en el host.
- Accesos a backups de máquinas virtuales.

## Referencias

- [0xdf — Moderators](https://0xdf.gitlab.io/2022/11/05/htb-moderators.html)
- [VirtualBox — Disk encryption](https://www.virtualbox.org/manual/ch09.html#diskencryption)
- [GitLab — pyvboxdie-cracker](https://gitlab.com/search?search=pyvboxdie-cracker)
- [Ficha Moderators](../../machines/linux/moderators/README.md)
