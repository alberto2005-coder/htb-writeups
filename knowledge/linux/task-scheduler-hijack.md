---
topic: Secuestro de tareas programadas
tags: [linux, cron, systemd, privesc, persistence, writable-scripts]
---

# Secuestro de tareas programadas

[🌐 English](task-scheduler-hijack.en.md) | **Español**

## Concepto

Un proceso privilegiado ejecuta periódicamente un script, binario o comando que un usuario de menos privilegios puede modificar. Al cambiar el contenido o la ruta referenciada, el atacante consigue ejecución con los privilegios de la tarea.

## Cuándo aplica

- `cron`, `systemd timers`, `at` o tareas de aplicaciones.
- Scripts en `/opt`, `/usr/local` o directorios de usuario con permisos de escritura.
- Comandos con rutas relativas o `PATH` manipulable.
- Tareas que restauran archivos automáticamente.

## Procedimiento

1. Enumerar tareas con `pspy`, `crontab -l`, `/etc/crontab` y `systemctl list-timers`.
2. Revisar propietario y permisos de cada script.
3. Comprobar si el contenido se restaura o se sobrescribe.
4. Sustituir el script por una acción controlada.
5. Esperar la ejecución y verificar el resultado.

```bash
pspy64 -pf -i 1000
ls -l /opt/backup.sh /usr/local/bin/*.py
find / -writable -type f 2>/dev/null | grep -E 'cron|systemd|/opt/'
```

## Variantes

- Script escribible por un grupo o por todos.
- Directorio escribible con un script que se invoca por ruta.
- `PATH` con un directorio controlado antes del binario legítimo.
- Wildcard de `tar` o `rsync` en un directorio escribible.
- Tarea que restaura el script original tras cada ejecución.

## Limitaciones

- La tarea debe ejecutarse con más privilegios.
- La restauración puede sobrescribir el cambio antes de la ejecución.
- SELinux/AppArmor puede impedir la escritura.
- La ventana entre ejecuciones puede ser larga.

## Mitigación y detección

- Guardar scripts en rutas no escribibles y con propietario root.
- Usar rutas absolutas y un `PATH` seguro.
- Monitorizar cambios en scripts de cron/systemd con `auditd`.
- Alertar de procesos inesperados lanzados por cron y de modificaciones en `/etc/cron*`.

## Referencias

- <https://attack.mitre.org/techniques/T1053/003/>
- <https://attack.mitre.org/techniques/T1053/006/>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html>
- <https://github.com/DominicBreuker/pspy>
