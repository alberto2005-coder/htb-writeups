---
sherlock: Cinder
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, registry, persistence, mft]
---

# Cinder — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Investigación de un host Windows con indicios de persistencia y ejecución no autorizada. Se combinan EVTX, hives de registro, prefetch y MFT para identificar el binario malicioso, el mecanismo de arranque y la cuenta utilizada.

## Escenario

Un equipo muestra actividad sospechosa después de un incidente. El equipo de respuesta recoge artefactos de triaje y pide determinar qué se ejecutó, cómo persistió y qué cuentas se vieron afectadas.

## Artefactos

- EVTX de Security, System y PowerShell.
- `NTUSER.DAT`, `SOFTWARE` y `SYSTEM`.
- Prefetch y `Amcache`.
- `$MFT` y archivos temporales.

## Metodología

1. Se revisan claves `Run`, `RunOnce`, servicios y tareas programadas.
2. Se identifica el binario y su ruta; se comprueba creación en `$MFT`.
3. Se correlaciona con prefetch/Amcache para confirmar ejecución.
4. Se revisan eventos 4688, 7045 y 4104.
5. Se documenta la cuenta, el proceso padre y la persistencia.

```bash
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run
EvtxECmd.exe -d C:\Evidence\evtx --csv C:\Evidence\out
PECmd.exe -d C:\Evidence\prefetch --csv C:\Evidence\pf
```

## Preguntas tipo

- ¿Qué binario se ejecutó de forma anómala?
- ¿Qué clave de registro o servicio lo inicia?
- ¿Qué cuenta lo ejecutó?
- ¿Cuándo se creó el archivo?
- ¿Se eliminaron artefactos después?

## Herramientas

`Registry Explorer`, `EvtxECmd`, `PECmd`, `MFTECmd`, `Timeline Explorer`.

## Evidencia y redacción

Se conservan capturas de las claves, eventos y línea temporal con usuarios y rutas redactados. No se publican respuestas literales.

## Lecciones aprendidas

- Las claves `Run` y los servicios son puntos de persistencia habituales.
- Prefetch y Amcache confirman ejecución incluso si falta el binario.
- El proceso padre ayuda a distinguir instalación legítima de abuso.
- La ausencia de un archivo no implica ausencia de ejecución.

## Detección

- Alertar de nuevos servicios y claves `Run` fuera de instaladores.
- Vigilar binarios en `AppData`/`ProgramData`.
- Correlacionar 7045 con creación de archivos.
- Revisar tareas programadas creadas fuera de ventana.

## Referencias

- <https://app.hackthebox.com/sherlocks/Cinder>
- <https://attack.mitre.org/techniques/T1547/001/>
- <https://attack.mitre.org/techniques/T1543/003/>
