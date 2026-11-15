---
topic: Escalada por script de backup en cron
tags: [linux, cron, backup, privesc, writable]
---

# Escalada por script de backup en cron

[🌐 English](cron-backup-privesc.en.md) | **Español**

## Concepto

Una tarea cron ejecuta como root un script de backup que el usuario puede modificar. Al añadir una línea, el siguiente ciclo ejecuta el comando con privilegios de root.

## Cuándo aplica

- Scripts de backup en `/usr/local/bin`, `/opt` o el home con permisos de escritura.
- Tareas cron o timers systemd que ejecutan scripts sin protección.
- Directorios de backup con wildcards o rutas controlables.

## Procedimiento

1. Enumerar cron y timers con `pspy`, `crontab -l` y `/etc/cron*`.
2. Revisar permisos y propietario de los scripts ejecutados.
3. Añadir una carga que copie bash con SUID o lance una shell.
4. Esperar la ejecución y usar la shell resultante.

```bash
pspy -f
ls -l /usr/bin/backup.sh /etc/cron.d/
printf 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash\n' >> /usr/bin/backup.sh
/tmp/rootbash -p
```

## Variantes

- `tar` con wildcard y checkpoint.
- `rsync` con `--rsh` o rutas controlables.
- Timer systemd con script escribible.
- PATH hijack dentro del script.

## Limitaciones

- El script debe ser escribible por el usuario.
- La tarea debe ejecutarse con root.
- El siguiente ciclo puede tardar.

## Mitigación y detección

- Scripts de backup propiedad de root y sin escritura para otros.
- Usar rutas absolutas y entornos limpios.
- Monitorizar cambios en scripts y procesos hijos de cron.

## Referencias

- <https://gtfobins.github.io/>
- <https://attack.mitre.org/techniques/T1053/003/>
- <https://man7.org/linux/man-pages/man5/crontab.5.html>
