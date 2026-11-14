---
topic: Crontab UI
tags: [linux, crontab-ui, cron, privesc, web-ui, scheduling]
---

# Crontab UI

[🌐 English](crontab-ui.en.md) | **Español**

## Concepto

Crontab UI es una interfaz web para gestionar tareas cron. Si se ejecuta como root y permite crear o editar trabajos, un usuario con acceso puede programar un comando privilegiado. El abuso no requiere una vulnerabilidad de memoria: es una funcionalidad expuesta con permisos excesivos.

## Cuándo aplica

- Crontab UI escuchando en localhost o en la red.
- Acceso sin autenticación o con credenciales débiles.
- Proceso ejecutado como root.
- Directorio de trabajos escribible.

## Procedimiento

1. Identificar el servicio y su usuario.
2. Revisar la autenticación y los trabajos existentes.
3. Crear una tarea que ejecute un comando inocuo.
4. Confirmar la ejecución como root.
5. Usar la tarea para leer archivos o establecer persistencia.

```bash
ps aux | grep -i crontab
crontab -l
curl -s http://127.0.0.1:8000/
```

## Variantes

- Panel sin autenticación.
- Credenciales por defecto.
- Trabajo que escribe en `/etc/sudoers` o lanza una shell.
- Persistencia mediante una tarea recurrente.

## Limitaciones

- El panel debe permitir crear o editar trabajos.
- El proceso debe ejecutarse con privilegios.
- La tarea puede tardar en ejecutarse.
- Algunos paneles restringen comandos.

## Mitigación y detección

- No ejecutar paneles de cron como root.
- Requerir autenticación y limitar comandos.
- Auditar cambios en crontabs y `/etc/cron.*`.
- Alertar de tareas nuevas con shells o escrituras sensibles.

## Referencias

- <https://github.com/alseambusher/crontab-ui>
- <https://attack.mitre.org/techniques/T1053/003/>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html>
