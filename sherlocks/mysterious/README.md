---
sherlock: Mysterious
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, scheduled-tasks, usb, lnk, registry]
---

# Mysterious — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Un usuario ejecuta un archivo desde un dispositivo extraíble y deja rastros en USBSTOR, LNK, prefetch y tareas programadas. Se reconstruye la secuencia de ejecución y el origen del archivo.

## Escenario

Un host presenta actividad no explicada por el usuario. Se entregan el hive `SYSTEM`, el perfil del usuario y artefactos de ejecución para determinar qué se conectó, qué se abrió y qué persistió.

## Artefactos

- `SYSTEM` (USBSTOR, MountedDevices).
- `NTUSER.DAT` (RecentDocs, UserAssist, RunMRU).
- LNK, jumplists y prefetch.
- Tareas programadas y EVTX.

## Metodología

1. Se identifican dispositivos USB por serial y volumen.
2. Se revisan LNK/jumplists para archivos abiertos desde el dispositivo.
3. Se confirma ejecución con prefetch/UserAssist.
4. Se buscan tareas o claves creadas tras la conexión.
5. Se ordena la línea temporal y se documenta el usuario.

```bash
reg query HKLM\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR /s
JLECmd.exe -d C:\\Evidence\\jumplist --csv C:\\Evidence\\out
PECmd.exe -d C:\\Evidence\\prefetch --csv C:\\Evidence\\pf
```

## Preguntas tipo

- ¿Qué dispositivo USB se conectó y cuándo?
- ¿Qué archivo se abrió desde él?
- ¿Qué usuario ejecutó el archivo?
- ¿Se creó persistencia después?
- ¿Hubo intento de borrado de rastros?

## Herramientas

`Registry Explorer`, `JLECmd`, `LECmd`, `PECmd`, `Timeline Explorer`.

## Evidencia y redacción

Se conservan capturas de las claves y la línea temporal con seriales, usuarios y rutas redactados.

## Lecciones aprendidas

- USBSTOR correlaciona dispositivo, serial y primeras conexiones.
- LNK y jumplists revelan archivos abiertos desde extraíbles.
- UserAssist/prefetch confirman ejecución.
- La persistencia puede crearse minutos después.

## Detección

- Alertar de ejecutables desde unidades extraíbles.
- Monitorizar creación de tareas tras conexión USB.
- Correlacionar 4688 con USBSTOR.
- Bloquear ejecución desde medios removibles.

## Referencias

- <https://app.hackthebox.com/sherlocks/Mysterious>
- <https://attack.mitre.org/techniques/T1091/>
- <https://attack.mitre.org/techniques/T1053/005/>
