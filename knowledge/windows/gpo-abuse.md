---
topic: GPO abuse
tags: [windows, active-directory, gpo, sharpgpoabuse, system, persistence]
---

# GPO abuse

[🌐 English](gpo-abuse.en.md) | **Español**

## Concepto

Un usuario con derechos para crear o modificar objetos de Directiva de Grupo puede añadir tareas, scripts o configuraciones que se aplican a equipos u OUs. Si la GPO alcanza un controlador de dominio o un servidor privilegiado, la tarea se ejecuta como SYSTEM y permite movimiento lateral o persistencia.

## Cuándo aplica

- Pertenencia a `Group Policy Creator Owners`.
- Derechos `WriteProperty` o `WriteDacl` sobre una GPO.
- OU de destino con equipos privilegiados.
- Capacidad de forzar `gpupdate` o esperar la aplicación.

## Procedimiento

1. Enumerar GPOs y permisos con BloodHound.
2. Identificar una OU o GPO modificable.
3. Crear una GPO o editar una existente.
4. Añadir una tarea inmediata o un script.
5. Aplicar la política y recibir la ejecución como SYSTEM.

```powershell
New-GPO -Name "upd-$(Get-Date -UFormat %s)"
.\SharpGPOAbuse.exe --addcomputertask --gponame <GPO> \
  --command powershell.exe --arguments "-EncodedCommand <B64>"
gpupdate /force
```

## Variantes

- Tarea inmediata en el arranque.
- Script de inicio o de cierre.
- Configuración de servicio o registro.
- Edición de una GPO existente con derechos delegados.

## Limitaciones

- Se necesitan permisos sobre la GPO o la OU.
- La política debe alcanzar el equipo objetivo.
- La aplicación puede requerir reinicio o `gpupdate`.
- Los controles de cambios y EDR pueden detectar la tarea.

## Mitigación y detección

- Auditar `Group Policy Creator Owners` y ACL de GPO.
- Restringir la edición de GPO a administradores de dominio.
- Monitorizar eventos 5136, 4662 y creación de tareas inmediatas.
- Revisar `gpupdate` y procesos hijos lanzados por GPO.

## Referencias

- <https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn581922(v=ws.11)>
- <https://github.com/Flangvik/SharpGPOAbuse>
- <https://attack.mitre.org/techniques/T1484/001/>
