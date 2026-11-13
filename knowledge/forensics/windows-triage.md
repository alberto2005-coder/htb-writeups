---
topic: Windows forensic triage
tags: [forensics, windows, mft, usn, shellbags, evtx, usb, jscript]
---

# Windows forensic triage

[🌐 English](windows-triage.en.md) | **Español**

## Concepto

El triaje de Windows combina artefactos de sistema de archivos, ejecución, registro y dispositivos para reconstruir una intrusión. `$MFT`, `$UsnJrnl`, Prefetch, EVTX, ShellBags y los registros USB permiten responder qué se ejecutó, cuándo y desde dónde.

## Cuándo aplica

- Imagen forense de un endpoint comprometido.
- Ejecución de un archivo comprimido o un script.
- Persistencia y movimiento lateral.
- Correlación de eventos y actividad de usuario.

## Procedimiento

1. Documentar zona horaria y hashes de la evidencia.
2. Generar un timeline con MFT, USN y Prefetch.
3. Revisar EVTX de Seguridad, Sistema, PowerShell y Sysmon.
4. Analizar ShellBags, LNK y registros USB.
5. Correlacionar procesos, archivos y cuentas.

```powershell
MFTECmd.exe -f "$MFT" --csv out --csvf mft.csv
MFTECmd.exe -f "$UsnJrnl" --csv out --csvf usn.csv
PECmd.exe -d C:\Windows\Prefetch --csv out --csvf prefetch.csv
EvtxECmd.exe -d Logs --csv out --csvf evtx.csv
```

## Variantes

- Ejecución mediante `wscript`/`cscript` y JScript.
- Archivo comprimido con LNK o acceso directo.
- USB como origen o exfiltración.
- Persistencia en tareas, servicios o WMI.

## Limitaciones

- Los timestamps pueden manipularse.
- Prefetch puede estar deshabilitado.
- Los logs pueden rotar o faltar.
- ShellBags no siempre registran la ruta completa.

## Mitigación y detección

- Habilitar auditoría y Sysmon con telemetría de procesos.
- Centralizar EVTX y proteger los logs.
- Restringir ejecución de scripts y dispositivos USB.
- Alertar de `wscript`, LNK, USN anómalo y creación de servicios.

## Referencias

- <https://ericzimmerman.github.io/>
- <https://attack.mitre.org/techniques/T1059/007/>
- <https://www.sans.org/white-papers/forensic-suite/>
