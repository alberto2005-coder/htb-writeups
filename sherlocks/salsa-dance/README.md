---
sherlock: Salsa Dance
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, mft, powershell, timeline]
---

# Salsa Dance — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; no se descargaron las evidencias originales.

## TL;DR

Caso DFIR de un host Windows comprometido. La investigación combina EVTX, MFT, historial de PowerShell y artefactos de ejecución para reconstruir el acceso inicial, la persistencia y la exfiltración. El objetivo es construir una línea temporal defendible y separar actividad legítima de la del intruso.

## Escenario

Una organización detecta actividad anómala en una estación de trabajo. Se entrega una colección de artefactos Windows y se solicita identificar el vector de entrada, las cuentas afectadas y los datos sustraídos.

## Artefactos

- EVTX de Security, System, PowerShell y Defender.
- `$MFT` y journals USN.
- Historial de PowerShell y prefetch.
- Artefactos de navegador y ejecución.
- Sin memoria ni disco completo.

## Metodología

1. Se inventarían los artefactos y se calculan hashes.
2. Se convierten los EVTX a CSV/JSON y se filtran por ventana temporal.
3. Se revisan 4624/4625, 4688, 4104 y 7045 para accesos, procesos, scripts y servicios.
4. Se cruza el `$MFT` con prefetch y USN para confirmar creación y ejecución.
5. Se revisan descargas, archivos temporales y conexiones salientes.
6. Se construye la línea temporal y se documentan huecos.

```bash
EvtxECmd.exe -d C:\Evidence\evtx --csv C:\Evidence\out
MFTECmd.exe -f C:\Evidence\$MFT --csv C:\Evidence\mft
```

## Preguntas tipo

- ¿Cuál fue el primer acceso y con qué cuenta?
- ¿Qué script de PowerShell se ejecutó y con qué propósito?
- ¿Qué mecanismo de persistencia se creó?
- ¿Qué archivos se comprimieron o exfiltraron?
- ¿Qué actividad es legítima y cuál es del atacante?

## Herramientas

`EvtxECmd`, `MFTECmd`, `Timeline Explorer`, `Chainsaw`, `jq`, `grep`.

## Evidencia y redacción

Se conservan capturas de los eventos y de la línea temporal con usuarios, IPs y rutas redactados. No se publican respuestas literales ni flags.

## Lecciones aprendidas

- La correlación EVTX/MFT/prefetch reduce falsos positivos.
- El historial de PowerShell y 4104 reconstruyen scripts.
- Los servicios 7045 son un indicador de persistencia.
- Una línea temporal sin huecos documentados es más útil que una lista de IOCs.

## Detección

- Alertar de 7045 con binarios fuera de `System32`.
- Correlacionar 4624 tipo 3/10 con horarios anómalos.
- Vigilar compresión y transferencias salientes.
- Revisar PowerShell con `-enc` y descargas HTTP.

## Referencias

- <https://app.hackthebox.com/sherlocks/SalsaDance>
- <https://attack.mitre.org/tactics/TA0003/>
- <https://learn.microsoft.com/en-us/powershell/scripting/windows-powershell/wmf/overview>
