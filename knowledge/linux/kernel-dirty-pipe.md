---
title: "DirtyPipe (CVE-2022-0847): escribir en la page cache"
tags: [linux, kernel, dirtypipe, cve-2022-0847, privesc, pipe]
---

# DirtyPipe (CVE-2022-0847): escribir en la page cache

[🇬🇧 English](kernel-dirty-pipe.en.md) | **Español**

## 1. Cuándo mirar aquí

Kernel Linux **5.8 o posterior** sin el parche de marzo de 2022. Un usuario sin privilegios puede sobrescribir ficheros de solo lectura, incluidos binarios SUID y ficheros de configuración, sin tocar el heap ni necesitar KASLR.

## 2. El fallo

Cuando `splice()` mueve una página de fichero a un pipe, el buffer del pipe conserva el flag `PIPE_BUF_FLAG_CAN_MERGE` de una operación anterior. Un `write()` posterior cree que puede fusionar datos con el buffer y escribe en la **page cache** del fichero, aunque el descriptor sea `O_RDONLY`.

```text
pipe lleno -> todos los buffers con CAN_MERGE
pipe vaciado -> los buffers se liberan, el flag queda
splice(fichero, offset-1, 1) -> buffer apunta a la página del fichero
write(payload) -> escribe en la page cache a partir de offset
```

Es una escritura de datos, no de estructuras del kernel: por eso no le afectan SMEP, SMAP, KASLR ni las mitigaciones de SLUB.

## 3. Versiones

- Afectados: 5.8 y posteriores, hasta 5.16.11, 5.15.25 y 5.10.102 (y ramas equivalentes).
- No afectados: < 5.8.
- En ramas EOL (5.9, por ejemplo) no hay parche: siguen vulnerables.

## 4. Límites

- No se puede escribir el byte 0 de una página (el `splice` debe mover al menos 1 byte).
- No se puede agrandar el fichero; solo sobrescribir dentro de su tamaño.
- El cambio vive en la page cache hasta que la página se expulsa o se reinicia.
- Escribir en un fichero mapeado puede corromper procesos que ya lo cargaron.

## 5. Usos típicos

1. **Binario SUID**: sobrescribir la entry o una función para lanzar un shell con SUID.
2. **`/etc/passwd`**: cambiar el hash de root y usar `su`; solo funciona si `su`/`login` son utilizables.
3. **`modprobe_path` por page cache**: si se puede escribir un binario que el kernel ejecute como root (`/sbin/modprobe`), se coloca shellcode en su entry y se dispara con un `binfmt` desconocido.
4. **Ficheros de configuración**: claves de SSH, cron, unidades systemd.

### Cadena con busybox y modprobe

- `/sbin/modprobe` suele ser un symlink a busybox.
- Entry point de busybox: `readelf -h`; offset en fichero = entry - base de carga.
- El offset no puede ser múltiplo de página.
- El fichero que dispara `request_module()` debe tener magic **no imprimible**; si los cuatro primeros bytes son ASCII imprimible, el kernel asume texto y no llama a modprobe.
- `call_usermodehelper()` ejecuta modprobe con stdout/stderr en `/dev/null`: el payload debe escribir en un fichero.
- Si el payload rompe busybox, `system()` y `/bin/sh` dejan de funcionar; usar syscalls directas.

## 6. Detección

- `splice` desde un fichero de solo lectura seguido de `write` al mismo pipe.
- Cambios de contenido en binarios del sistema sin escritura previa del fichero (integridad, IMA, `rpm -Va`).
- `modprobe_path` modificado y ejecuciones de `/sbin/modprobe` sin carga de módulo real.
- Ejecución de ficheros con magic no imprimible o `binfmt-*` invocados desde un proceso de usuario.
- Page cache con páginas modificadas que no coinciden con el hash en disco.

## 7. Mitigación

- Actualizar a 5.16.11, 5.15.25, 5.10.102 o posterior; no hay workaround fiable.
- No ejecutar binarios desde rutas escribibles; montar `/usr` y `/bin` en solo lectura ayuda a detectar, no a prevenir.
- Integridad de binarios y de `modprobe_path`; auditar `request_module`.
- Containers: el bug permite escapar de la imagen al host si comparten kernel vulnerable.

CWE-665 (improper initialization), MITRE T1068 (exploitation for privilege escalation). Referencias: dirtypipe.cm4all.com, NVD CVE-2022-0847 y el aviso de CISA.
