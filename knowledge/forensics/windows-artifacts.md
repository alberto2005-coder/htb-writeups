---
title: Artefactos Windows — EVTX, MFT, Prefetch y Sysmon
tags: [forensics, windows, dfir, evtx, mft, sysmon]
---

# Artefactos Windows: qué mirar y con qué

[🇬🇧 English](windows-artifacts.en.md) | **Español**

## 1. Orden de trabajo

1. **Línea temporal** de ejecución y logins (Prefetch, EVTX, MFT).
2. **Persistencia** (servicios, tareas, Run keys, WMI).
3. **Movimiento lateral** (4624 tipo 3/10, 5140, SMB, RDP).
4. **Exfiltración** (Sysmon 3, DNS, navegador).

Herramientas de referencia: la suite de Eric Zimmerman (`EvtxECmd`, `MFTECmd`, `PECmd`, `AmcacheParser`, `AppCompatCacheParser`) y `Timeline Explorer` para correlacionar. `Hayabusa` resume EVTX con reglas Sigma.

## 2. EVTX: eventos que importan

| Evento | Qué dice |
|---|---|
| 4624 | logon correcto; **tipo 3** red, **tipo 10** RDP |
| 4625 | fallo de logon (fuerza bruta, spray) |
| 4648 | credenciales explícitas (`runas`) |
| 4672 | privilegios especiales asignados |
| 4688 | proceso creado (con línea de comandos si está activado) |
| 4720/4732 | usuario creado / añadido a grupo |
| 4769 | TGS solicitado (RC4 `0x17` = Kerberoasting) |
| 4662 | acceso a objetos AD (DCSync: `DS-Replication-Get-Changes`) |
| 5140/5145 | acceso a recurso compartido |
| 7045 | servicio instalado |
| 4698 | tarea programada creada |
| 4104 | script block de PowerShell |
| 1102 | log borrado |

```bash
EvtxECmd.exe -d C:\Evidence\Windows\System32\winevt\Logs --csv C:\Out --csvf evtx.csv
Hayabusa.exe csv-timeline -d C:\Evidence\Logs -o timeline.csv
```

## 3. MFT y timestamps

`$MFT` da nombre, tamaño, flags y cuatro timestamps por fichero. `MFTECmd` lo convierte en CSV:

```bash
MFTECmd.exe -f '$MFT' --csv C:\Out --csvf mft.csv
```

- **Timestomping**: `$STANDARD_INFORMATION` anterior a `$FILE_NAME` o ambos incoherentes con el `$LogFile`/`UsnJrnl`.
- **Zone.Identifier**: ADS con la URL de origen de un fichero descargado.
- **Ficheros residentes**: contenido dentro de la propia entrada MFT (útil para scripts pequeños).

## 4. Ejecución y persistencia

- **Prefetch** (`PECmd`): ejecutables, conteo, última ejecución, ficheros abiertos.
- **Amcache**: ejecutables y hashes vistos.
- **Shimcache/AppCompatCache**: ejecutables que existieron, sin fecha fiable.
- **Run keys**: `HKLM\...\CurrentVersion\Run`, `RunOnce`, tareas (`.job`), servicios (`ImagePath`).
- **WMI**: suscripciones en `root\subscription` (persistencia sin fichero).
- **PSReadLine**: `ConsoleHost_history.txt` con comandos del usuario.

## 5. Correlación

Un solo artefacto no prueba nada. Patrón típico:

```text
Prefetch de powershell.exe  →  4104 con el script  →  4688 del hijo  →  5140 al share
```

Cruza siempre **dos fuentes** y anota la ruta exacta de cada evidencia. En Sherlocks, la respuesta suele estar en el cruce, no en el evento aislado.

## 6. Errores típicos

- **`EvtxECmd` no lee un `.evtx`** → está corrupto o es un `.evtx` de otra versión; prueba `wevtutil epl` desde un Windows.
- **Fechas en UTC y en local mezcladas** → normaliza todo a UTC antes de comparar.
- **`$MFT` sin nombres** → necesitas también `$UsnJrnl` o el `$LogFile` para resolver renombrados.
- **Prefetch vacío** → el volumen no tenía Prefetch activado o el disco es SSD con la directiva deshabilitada.
- **Timestomp «perfecto»** → mira `$FILE_NAME` y el orden de las entradas MFT, no solo `$STANDARD_INFORMATION`.

## 7. Detección y mitigación

- Activar auditoría de proceso (4688 con línea de comandos), PowerShell (4104) y Sysmon.
- Centralizar EVTX con reenvío y retención suficiente.
- Monitorizar 7045/4698 y cambios en Run keys; alertar de 1102.
- Usar `$MFT` + `UsnJrnl` para integridad de timestamps.

MITRE: T1070.006 (timestomp), T1059.001, T1543, T1053.
