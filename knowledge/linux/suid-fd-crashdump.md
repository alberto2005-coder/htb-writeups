---
topic: SUID — lectura por descriptores y crash dumps
tags: [linux, suid, file-descriptors, core-dump, crash, secret, privesc]
---

# SUID — lectura por descriptores y crash dumps

[🌐 English](suid-fd-crashdump.en.md) | **Español**

## Concepto

Un binario SUID que abre un archivo privilegiado y no cierra el descriptor permite acceder a él por `/proc/<PID>/fd/<N>`. Los permisos del archivo siguen aplicando: sirve para leer archivos legibles dentro de directorios sin permiso de traversal, no para saltarse un modo 400. Si además genera un core dump, el contenido leído como root queda en el volcado, que puede ser legible. En Secret, `count` permitía leer `/root/.profile` por el descriptor; `root.txt` aparecía en el crash dump.

## Cuándo aplica

- Un binario SUID abre archivos que el usuario no puede leer.
- El proceso deja descriptores abiertos o ejecuta un hijo.
- Los core dumps están habilitados y se escriben en una ruta accesible.
- `kernel.core_pattern` o `apport` no restringen el volcado.

## Procedimiento

1. Identificar el SUID y su código fuente si está disponible.
2. Ejecutarlo con un archivo privilegiado y observar `/proc`.
3. Leer `/proc/<PID>/fd/<N>` si el modo del archivo lo permite.
4. Alternativamente, provocar un crash y localizar el core.
5. Extraer el contenido con `strings` o `grep`.

## Comandos

```bash
/opt/count
ls -l /proc/<PID>/fd/
cat /proc/<PID>/fd/<N>  # solo si el archivo es legible por el usuario
```

```bash
ulimit -c unlimited
cat /proc/sys/kernel/core_pattern
ls -l /var/crash/
strings /var/crash/_opt_count.*.crash | grep -i 'flag\|root'
```

## Variantes

- `/proc/<PID>/maps` y `mem` si hay permisos.
- `gdb -p <PID>` para adjuntarse a un proceso SUID.
- `ptrace` sobre un hijo si el binario lo permite.
- Core dump generado por `abort()` o por una violación de segmento.
- `apport` en Ubuntu escribe en `/var/crash` con permisos controlados.

## Limitaciones

- `fs.suid_dumpable` puede impedir el core de un SUID.
- `core_pattern` puede enviar el volcado a un pipe o a una ruta no accesible.
- El descriptor puede cerrarse antes de poder leerlo.
- `ptrace` puede estar restringido por `yama`.
- El binario puede limpiar el archivo temporal.

## Mitigación

- Cerrar descriptores antes de ejecutar código o de salir.
- Configurar `fs.suid_dumpable=0` y `core_pattern` seguro.
- Limitar `ptrace` con `kernel.yama.ptrace_scope`.
- Retirar SUID innecesarios y revisar los que abren archivos.
- Usar `O_CLOEXEC` en los descriptores.

## Detección

- Lecturas de `/proc/<PID>/fd` por usuarios no propietarios.
- Core dumps de procesos SUID.
- `gdb` o `strace` adjuntos a binarios privilegiados.
- Cambios en `core_pattern` o `ulimit`.
- Accesos a `/var/crash` con contenido sensible.

## Referencias

- [0xdf — Secret](https://0xdf.gitlab.io/2022/03/26/htb-secret.html)
- [Linux — proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Linux — core(5)](https://man7.org/linux/man-pages/man5/core.5.html)
- [Ficha Secret](../../machines/linux/secret/README.md)
