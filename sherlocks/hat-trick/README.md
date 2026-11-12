---
sherlock: Hat Trick
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, scheduled-tasks, credential-access, timeline]
---

# Hat Trick — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Caso DFIR Windows centrado en la creación de tareas programadas y acceso a credenciales. Los EVTX, el registro y el MFT permiten identificar el binario, la tarea persistente, la cuenta usada y el momento del incidente.

## Escenario

Un host presenta alertas de persistencia y ejecución fuera de horario. Se entrega una colección de triaje y se pide reconstruir la cadena y el impacto.

## Artefactos

- Security/System/TaskScheduler EVTX.
- `SOFTWARE` y `NTUSER.DAT`.
- `C:\Windows\System32\Tasks`.
- Prefetch, Amcache y `$MFT`.

## Metodología

1. Se revisan tareas programadas y su historial (106/200/201).
2. Se identifican binarios en rutas de usuario y se confirma su creación.
3. Se cruzan 4624/4688 con la ejecución de la tarea.
4. Se revisan accesos a LSASS/SAM y herramientas de credenciales.
5. Se documenta la persistencia y se elimina en el análisis.

```bash
schtasks /query /fo LIST /v
EvtxECmd.exe -d C:\Evidence\evtx --csv C:\Evidence\out
```

## Preguntas tipo

- ¿Qué tarea se creó y con qué nombre?
- ¿Qué binario ejecuta y desde qué ruta?
- ¿Qué cuenta la creó?
- ¿Cuándo se ejecutó por primera vez?
- ¿Hubo acceso a credenciales?

## Herramientas

`EvtxECmd`, `Autoruns`, `Timeline Explorer`, `PECmd`, `MFTECmd`.

## Evidencia y redacción

Se conservan capturas de tareas y eventos con usuarios y rutas redactados. No se publican respuestas literales.

## Lecciones aprendidas

- Las tareas programadas son persistencia sigilosa y frecuente.
- El historial de TaskScheduler confirma ejecuciones.
- Binarios en `AppData`/`ProgramData` merecen revisión.
- La correlación con 4624 identifica la cuenta.

## Detección

- Alertar de tareas creadas fuera de inventario.
- Vigilar acciones que ejecutan scripts en rutas de usuario.
- Correlacionar 4698/106 con procesos hijos.
- Revisar accesos a LSASS y SAM.

## Referencias

- <https://app.hackthebox.com/sherlocks/HatTrick>
- <https://attack.mitre.org/techniques/T1053/005/>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4698>
