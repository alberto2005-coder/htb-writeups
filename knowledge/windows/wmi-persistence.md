---
topic: WMI persistence
tags: [windows, wmi, persistence, event-consumer, sysmon, dfir]
---

# WMI persistence

[🌐 English](wmi-persistence.en.md) | **Español**

## Concepto

WMI permite registrar una suscripción permanente que ejecuta una acción cuando ocurre un evento. La cadena típica combina `__EventFilter`, `CommandLineEventConsumer` y `FilterToConsumerBinding`; el consumidor se ejecuta con los privilegios del servicio WMI y sobrevive a reinicios.

## Cuándo aplica

- Persistencia sin un servicio o tarea convencional.
- Ejecución recurrente por eventos del sistema.
- Sospecha de un consumidor WMI malicioso.
- Análisis de Sysmon o del repositorio WMI.

## Procedimiento

1. Enumerar filtros, consumidores y bindings.
2. Revisar nombres, consultas y líneas de comando.
3. Correlacionar con Sysmon 19, 20 y 21.
4. Comparar con el software legítimo instalado.
5. Eliminar la suscripción y preservar la evidencia.

```powershell
Get-WmiObject -Namespace root\Subscription -Class __EventFilter
Get-WmiObject -Namespace root\Subscription -Class CommandLineEventConsumer
Get-WmiObject -Namespace root\Subscription -Class __FilterToConsumerBinding
```

## Variantes

- Consumidor de línea de comandos.
- Consumidor de script o ActiveScript.
- Filtro basado en proceso, registro o tiempo.
- Persistencia en el repositorio WMI.

## Limitaciones

- El repositorio puede requerir privilegios altos.
- Sysmon debe tener los eventos habilitados.
- Herramientas legítimas también usan WMI.
- La eliminación sin evidencia previa destruye pruebas.

## Mitigación y detección

- Auditar el namespace `root\Subscription`.
- Habilitar Sysmon 19–21 y centralizar eventos.
- Restringir creación de suscripciones WMI.
- Alertar de consumidores con PowerShell, `cmd` o rutas de usuario.

## Referencias

- <https://learn.microsoft.com/en-us/windows/win32/wmisdk/receiving-a-wmi-event>
- <https://attack.mitre.org/techniques/T1546/003/>
- <https://www.sans.org/white-papers/wmi-forensics/>
