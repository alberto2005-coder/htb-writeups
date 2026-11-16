---
topic: 7-Zip — wildcard y listas @ para leer archivos
tags: [linux, 7z, wildcard, listfile, file-read, privesc]
---

# 7-Zip — wildcard y listas @ para leer archivos

[🌐 English](7z-wildcard-file-read.en.md) | **Español**

## Concepto

`7za` interpreta un argumento que empieza por `@` como una lista de archivos y muestra los errores al leerla. Si un script root ejecuta `7za ... -- *`, se puede crear `@lista` y un symlink con el mismo nombre para filtrar el contenido del destino.

## Cuándo aplica

- Un script root usa `7za` con un wildcard.
- El directorio de trabajo es escribible.
- `--` no desactiva el procesamiento de `@`.

## Procedimiento

1. Identificar el comando y el directorio.
2. Crear `@x` y un symlink `x` al archivo objetivo.
3. Ejecutar el script root.
4. Reconstruir el archivo desde los mensajes de error.

## Comandos

```bash
touch @0xdf; ln -fs /root/.ssh/id_rsa 0xdf
sudo usage_management
# limpiar ' : No more files' y reconstruir la clave
```

## Variantes

- Listas `@` con varios archivos.
- Symlinks a `/etc/shadow` o configuraciones.
- Combinar con `tar` o `rsync` con wildcard.

## Limitaciones

- El script puede usar rutas absolutas sin wildcard.
- `7za` moderno puede cambiar el tratamiento de `@`.
- El directorio puede no ser escribible.

## Mitigación

- Evitar wildcards; usar `find -print0` y `xargs -0`.
- No ejecutar backups como root.
- Usar `--` y validar nombres de archivo.

## Detección

- Archivos `@*` en directorios de backup.
- Errores de `7za` con contenido de archivos.
- Ejecuciones de backup fuera de horario.

## Caso CTF: listfile en un backup periódico

En CTF, `/backup/backup.sh` ejecuta cada minuto `7za a /backup/$filename.zip -t7z -snl -p$pass -- *` desde un directorio escribible. Se crea un archivo `@0xdf` y un symlink `0xdf` a `/root/root.txt`; el wildcard expande `@0xdf`, `7za` lo interpreta como lista y el error incluye el contenido del destino. El script borra el log al terminar, así que conviene seguirlo con `tail -f` desde otra sesión.

```bash
touch @0xdf
ln -fs /root/root.txt 0xdf
# esperar la ejecución del cron y revisar el log antes de que se borre
```

La misma idea funciona si el script comprime un directorio completo con `*` y el atacante puede crear archivos allí. La clave está en que `@` se procesa incluso después de `--`.

## Referencias

- [HackTricks — 7z wildcard](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/wildcards-spare-tricks.html)
- [0xdf — Usage](https://0xdf.gitlab.io/2024/08/10/htb-usage.html)
- [p7zip — command line](https://p7zip.sourceforge.net/)
- [0xdf — CTF](https://0xdf.gitlab.io/2019/07/20/htb-ctf.html)
- [7-Zip — command line](https://7-zip.org/)
