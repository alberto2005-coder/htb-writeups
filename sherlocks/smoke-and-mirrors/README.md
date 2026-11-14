---
sherlock: Smoke & Mirrors
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, evtx, powershell, sysmon, amsi, lsass]
---

# Smoke & Mirrors — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Operation Blackout 2025. Un equipo Windows muestra actividad PowerShell ofuscada y cambios de defensas. Se entregan EVTX y se pide reconstruir la ejecución, la persistencia y la evasión.

## Evidencias

- `Security.evtx`, `PowerShell Operational.evtx`, `Sysmon.evtx` y `System.evtx`.
- No se entrega memoria ni disco completo.

```bash
EvtxECmd.exe -d . --csv out
chainsaw hunt . -s sigma/
```

## Investigación

### 1. Inventario y triaje

Se cargan los canales en Timeline Explorer y se ordenan por tiempo. Los eventos 4104 (Script Block) y Sysmon 1 (process creation) dan la primera línea temporal.

- PowerShell 4104 con bloques codificados o `IEX`.
- Sysmon 1 con `powershell.exe` y argumentos inusuales.
- Sysmon 13 para cambios de registro.

### 2. Línea temporal

Se normaliza la zona horaria y se correlacionan:
- Inicio del proceso y usuario.
- Descarga o decodificación del script.
- Creación de servicio/tarea o clave `Run`.
- Intentos de desactivar AMSI, Defender o protección LSA.

```bash
Get-WinEvent -Path 'PowerShell Operational.evtx' -FilterXPath "*[System[EventID=4104]]"
```

### 3. Artefacto clave

El bloque 4104 reconstruye el script. Se decodifica base64, se resuelven las variables y se identifican las llamadas a `AmsiScanBuffer`, `VirtualProtect` o `lsass`. La clave de registro o el servicio confirman persistencia.

## Conclusiones

- El atacante ejecutó PowerShell ofuscado y manipuló defensas.
- La persistencia quedó en registro/servicio, según el artefacto.
- Los IOC incluyen rutas, nombres de proceso y claves modificadas.
- La evidencia permite escribir detecciones para 4104 y Sysmon.

## Lecciones

- 4104 es esencial cuando no hay memoria.
- La evasión de AMSI deja rastros en el script y en las llamadas.
- Sin disco, la persistencia se confirma por registro y servicios.

## Referencias

- <https://www.hackthebox.com/sherlocks/Smoke%20%26%20Mirrors>
- <https://attack.mitre.org/techniques/T1059/001/>
- <https://attack.mitre.org/techniques/T1562/001/>
