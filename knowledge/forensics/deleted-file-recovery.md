---
topic: Recuperación de archivos borrados
tags: [forensics, deleted-files, carving, ntfs, ext4, usb, photorec]
---

# Recuperación de archivos borrados

[🌐 English](deleted-file-recovery.en.md) | **Español**

## Concept

Al borrar un archivo, el sistema libera sus bloques pero no siempre los sobrescribe. Los metadatos y el contenido pueden recuperarse de espacio no asignado, de la papelera, de journals o de un dispositivo extraíble, siempre que no se haya reutilizado el espacio.

## Cuándo aplica

- Archivos eliminados en NTFS, ext4, FAT o exFAT.
- Dispositivos USB o imágenes de disco.
- Recuperación de flags o documentos borrados.
- Análisis de un equipo tras un incidente.

## Procedimiento

1. Crear una imagen forense y trabajar sobre una copia.
2. Montar en solo lectura o usar herramientas de recuperación.
3. Revisar la papelera, `$Recycle.Bin` o `.Trash`.
4. Buscar metadatos y entradas no asignadas.
5. Hacer carving por firmas si los metadatos no bastan.

```bash
dd if=/dev/sdb of=usb.img bs=4M status=progress
photorec usb.img
fls -r -p usb.img | grep -i deleted
```

## Variantes

- Recuperación desde la MFT de NTFS.
- `extundelete` o `debugfs` en ext4.
- Carving de PDF, ZIP o imágenes por cabecera.
- Archivos en la papelera o en puntos de restauración.
- Recuperación de un USB formateado.

## Limitaciones

- El espacio reutilizado destruye el contenido.
- Algunos sistemas cifran el disco.
- El carving puede producir falsos positivos.
- Montar el dispositivo en escritura altera la evidencia.

## Mitigación y detección

- Cifrar discos y dispositivos extraíbles.
- Usar borrado seguro cuando corresponda.
- Auditar la creación de imágenes y el acceso a la papelera.
- Preservar la cadena de custodia y los hashes.

## Referencias

- <https://www.cgsecurity.org/wiki/PhotoRec>
- <https://forensics.wiki/deleted_file_recovery/>
- <https://attack.mitre.org/techniques/T1070/004/>
- <https://csrc.nist.gov/publications/detail/sp/800-86/final>
