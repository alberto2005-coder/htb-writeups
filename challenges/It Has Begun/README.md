---
challenge: It Has Begun
type: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, windows, powershell, evtx, logs]
---

# It Has Begun — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Se entrega un conjunto de registros de Windows tras una intrusión. El análisis de PowerShell, eventos de proceso y líneas de tiempo revela el comando que ejecutó el atacante y conduce a la flag.

## Enunciado y superficie

- Forensics, Very Easy, retirado.
- Se entrega un archivo comprimido con artefactos de Windows.
- El objetivo es reconstruir la actividad inicial.

```bash
unzip evidence.zip -d evidence
find evidence -type f -maxdepth 3
```

## Reconocimiento

```bash
file evidence/*
sha256sum evidence/*
```

- Hay archivos EVTX, transcripciones o un volcado de eventos.
- Los nombres y timestamps sitúan la actividad.
- Se documenta la cadena de custodia antes de abrir nada.

## Análisis

Se cargan los EVTX con `EvtxECmd` o `Get-WinEvent`. Se filtran eventos de PowerShell (4103/4104), creación de procesos (4688) y servicios. La secuencia muestra el comando, el usuario y el host.

```powershell
Get-WinEvent -Path .\Security.evtx -FilterXPath "*[System[EventID=4688]]"
```

## Explotación

No hay explotación remota: se responde a las preguntas del reto con la evidencia. La flag se obtiene al reconstruir el comando o el nombre del artefacto; no se publica.

```bash
EvtxECmd.exe -f Security.evtx --csv out
```

## Evidencia

- Eventos de PowerShell y procesos correlacionados.
- Usuario, host y hora del comando.
- Línea de tiempo coherente con el escenario.

## Lecciones aprendidas

- Los EVTX conservan mucho más que errores.
- PowerShell y creación de procesos se complementan.
- La línea de tiempo reduce el ruido.
- La cadena de custodia empieza antes del análisis.

## Mitigaciones y detección

- Habilitar Script Block Logging y auditar procesos.
- Centralizar logs y proteger su integridad.
- Alertar de PowerShell con comandos codificados.
- Revisar retención y acceso a los registros.
- Referencias: SANS Windows Forensics, EvtxECmd.

## Referencias

- <https://www.hackthebox.com/challenges/It%20Has%20Begun>
- <https://github.com/EricZimmerman/EvtxECmd>
- <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows>
- <https://attack.mitre.org/techniques/T1059/001/>
