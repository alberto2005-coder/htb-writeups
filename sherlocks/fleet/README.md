---
sherlock: Fleet
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, fleet, evtx, lateral-movement, timeline]
---

# Fleet — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Investigación de una flota de endpoints Windows. Se comparan artefactos de varios hosts para identificar el primero comprometido, el movimiento lateral y los sistemas afectados. La clave es normalizar la línea temporal entre equipos y no analizar cada host de forma aislada.

## Escenario

Varios equipos de una organización muestran alertas relacionadas. Se entrega una colección de triaje de la flota y se solicita determinar el alcance, el origen y la propagación.

## Artefactos

- EVTX de Security/System por host.
- Prefetch, Amcache y `$MFT`.
- Listados de procesos y conexiones.
- Usuarios locales y tareas programadas.
- Inventario de la flota.

## Metodología

1. Se inventarían hosts, nombres y fechas de recolección.
2. Se normalizan zonas horarias y se crea una línea temporal común.
3. Se buscan logons 4624 tipo 3/10 y accesos SMB/WinRM entre hosts.
4. Se comparan procesos y binarios con el inventario legítimo.
5. Se identifica el host paciente cero y el orden de propagación.
6. Se documentan cuentas comprometidas y sistemas no afectados.

```bash
EvtxECmd.exe -d C:\Fleet\Host01\evtx --csv C:\Fleet\out\host01
PECmd.exe -d C:\Fleet\Host01\prefetch --csv C:\Fleet\out\pf01
```

## Preguntas tipo

- ¿Qué host se comprometió primero?
- ¿Qué cuentas se usaron para el movimiento lateral?
- ¿Qué binario o servicio se propagó?
- ¿Qué hosts quedaron afectados?
- ¿Qué actividad es anterior al incidente?

## Herramientas

`EvtxECmd`, `PECmd`, `MFTECmd`, `Timeline Explorer`, `jq`.

## Evidencia y redacción

Se conservan capturas de la línea temporal multi-host con nombres, IPs y cuentas redactados. No se publican respuestas literales.

## Lecciones aprendidas

- La flota se analiza como un conjunto, no host por host.
- Las zonas horarias deben normalizarse antes de comparar.
- WinRM/SMB dejan rastros en origen y destino.
- El inventario legítimo reduce falsos positivos.

## Detección

- Correlacionar 4624 tipo 3/10 entre estaciones.
- Alertar de creación de servicios en varios hosts.
- Vigilar propagación de binarios por SMB.
- Mantener inventario y línea base de procesos.

## Referencias

- <https://app.hackthebox.com/sherlocks/Fleet>
- <https://attack.mitre.org/tactics/TA0008/>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624>
