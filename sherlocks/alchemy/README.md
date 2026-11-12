---
sherlock: Alchemy
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, powershell, credential-access, scheduled-task, evtx]
---

# Alchemy — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Un host Windows muestra ejecución ofuscada de PowerShell y acceso a credenciales. Se reconstruye la cadena con 4104, 4688, tareas programadas y artefactos de memoria/registro.

## Escenario

Se detecta una tarea programada que lanza PowerShell con una carga codificada. El equipo de respuesta entrega logs y artefactos para identificar el propósito y el alcance.

## Artefactos

- PowerShell Operational (4103/4104).
- Security (4688, 4672, 4624).
- Task Scheduler y registro.
- `$MFT`, prefetch y memoria.

## Metodología

1. Se decodifica la carga de PowerShell y se identifican funciones y URLs.
2. Se revisa el proceso padre y la cuenta que creó la tarea.
3. Se buscan accesos a LSASS/SAM y volcados.
4. Se correlaciona con creación de archivos y conexiones de red.
5. Se documenta la persistencia y el impacto.

```bash
EvtxECmd.exe -f 'Microsoft-Windows-PowerShell%4Operational.evtx' --csv C:\\Evidence\\ps
Get-ScheduledTask | Export-Csv tasks.csv
```

## Preguntas tipo

- ¿Qué tarea programa la ejecución?
- ¿Qué hace la carga ofuscada?
- ¿Qué credenciales o bases de datos accede?
- ¿Qué usuario la creó?
- ¿Se exfiltraron datos?

## Herramientas

`EvtxECmd`, `PowerShell Log Parser`, `Timeline Explorer`, `Volatility`, `PECmd`.

## Evidencia y redacción

Se conservan capturas de la carga decodificada y la línea temporal con usuarios, rutas y dominios redactados.

## Lecciones aprendidas

- 4104 es clave para PowerShell ofuscado.
- Las tareas programadas son persistencia y ejecución.
- El acceso a LSASS deja eventos y handles.
- La decodificación debe hacerse en entorno aislado.

## Detección

- Alertar de PowerShell con `-enc` y tareas nuevas.
- Monitorizar acceso a LSASS por procesos no firmados.
- Correlacionar 4104 con 4688 y red.
- Restringir creación de tareas a administradores.

## Referencias

- <https://app.hackthebox.com/sherlocks/Alchemy>
- <https://attack.mitre.org/techniques/T1059/001/>
- <https://attack.mitre.org/techniques/T1053/005/>
