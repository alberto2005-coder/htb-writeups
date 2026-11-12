---
sherlock: LATUS
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, timeline, evtx, mft, registry]
---

# LATUS — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Investigación multi-artefacto de un host Windows. Se combinan EVTX, MFT, registro y ejecución para reconstruir el acceso, la persistencia y el movimiento lateral.

## Escenario

Un servidor muestra señales de compromiso en varios artefactos. El equipo de respuesta pide una línea temporal única y la atribución de cada acción.

## Artefactos

- `Security.evtx`, `System.evtx`, PowerShell.
- `$MFT`, `$UsnJrnl`, prefetch y Amcache.
- Hives `SYSTEM`, `SOFTWARE`, `NTUSER.DAT`.
- Logs de aplicaciones y red.

## Metodología

1. Se inventarían los artefactos y se fijan zonas horarias.
2. Se construye una línea temporal con EVTX/MFT.
3. Se identifican procesos, servicios y tareas anómalas.
4. Se cruzan cuentas y conexiones de red.
5. Se separa actividad legítima de la del atacante.

```bash
EvtxECmd.exe -d C:\\Evidence\\evtx --csv C:\\Evidence\\out
MFTECmd.exe -f C:\\Evidence\\MFT --csv C:\\Evidence\\mft
TimelineExplorer.exe
```

## Preguntas tipo

- ¿Cuál fue el primer indicio de acceso?
- ¿Qué cuenta se utilizó?
- ¿Qué persistencia se creó?
- ¿Qué hosts se contactaron?
- ¿Qué datos se accedieron?

## Herramientas

`EvtxECmd`, `MFTECmd`, `Registry Explorer`, `Timeline Explorer`, `Chainsaw`.

## Evidencia y redacción

Se conservan capturas de la línea temporal y hashes con usuarios, IPs y rutas redactados.

## Lecciones aprendidas

- Una sola fuente no basta para atribuir.
- La zona horaria mal aplicada rompe la secuencia.
- Los artefactos de ejecución confirman lo que los logs insinúan.
- La correlación multi-host revela movimiento lateral.

## Detección

- Correlacionar 4624/4688/7045 en ventanas cortas.
- Alertar de servicios y tareas nuevas.
- Revisar accesos a admin shares.
- Mantener retención suficiente de EVTX.

## Referencias

- <https://app.hackthebox.com/sherlocks/LATUS>
- <https://attack.mitre.org/techniques/T1053/>
- <https://attack.mitre.org/techniques/T1021/>
