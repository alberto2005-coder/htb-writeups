---
challenge: Event Horizon
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, windows, evtx, powershell, event-logs]
---

# Event Horizon — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin flag real.

## TL;DR

Se entrega una colección de EVTX de un equipo Windows comprometido. Los logs clásicos de PowerShell fueron borrados, pero quedan eventos operacionales y de scripting que permiten reconstruir el comando y la flag. Hay que parsear todos los EVTX, no solo `Microsoft-Windows-PowerShell`.

## Enunciado y superficie

- Forensics, Easy, retirado.
- Directorio `Logs/` con cientos de EVTX.
- Carpeta `TraceFormat` auxiliar.
- El enunciado dice que los logs de PowerShell fueron limpiados.

```bash
find Logs -name '*.evtx' | wc -l
```

## Reconocimiento

Se listan los canales y se buscan los relacionados con PowerShell, WMI y scripting:

```bash
find Logs -iname '*PowerShell*' -o -iname '*WMI*'
```

```text
Microsoft-Windows-PowerShell%4Operational.evtx
Microsoft-Windows-PowerShell%4Admin.evtx
Microsoft-Windows-WMI-Activity%4Operational.evtx
```

## Análisis del código

No hay binario: el artefacto es el EVTX. Se convierte a XML/JSON con `evtx_dump.py` o `EvtxECmd`:

```bash
python3 evtx_dump.py 'Logs/Microsoft-Windows-PowerShell%4Operational.evtx' > ps.xml
grep -iE 'ScriptBlock|4104|CommandLine|flag' ps.xml | head
```

También se puede usar Chainsaw con reglas Sigma para localizar ejecución sospechosa.

## Explicación del fallo

Borrar los logs de PowerShell no elimina los eventos operacionales ya escritos ni las copias en otros canales. El atacante confía en una limpieza parcial; el analista debe revisar todos los EVTX y los eventos de scripting (4104).

## Reproducción local

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install python-evtx
python3 evtx_dump.py 'Logs/Microsoft-Windows-PowerShell%4Operational.evtx' > ps.xml
```

Se busca el script block, se decodifica si está en base64 y se extrae la flag. El resultado se verifica en la plataforma.

## Explotación

No hay servidor. La explotación es forense: reconstruir el comando a partir de los eventos y decodificar el payload. La flag se redacta.

## Evidencia

- Número de EVTX y canales relevantes.
- Evento 4104 con el script redactado.
- Flag redactada.

## Lecciones aprendidas

- Los logs operacionales sobreviven al borrado de los logs clásicos.
- 4104 registra bloques de script y es clave para PowerShell.
- Hay que revisar WMI y Task Scheduler, no solo PowerShell.
- La limpieza de logs es selectiva y deja rastros.

## Mitigaciones y detección

- Centralizar logs en un SIEM antes de que el atacante pueda borrarlos.
- Habilitar Script Block Logging y transcripción.
- Alertar de 1102 (log clearing) y de ausencias repentinas.
- Restringir permisos para limpiar logs.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/event-horizon/>
- <https://github.com/williballenthin/python-evtx>
- <https://attack.mitre.org/techniques/T1070/001/>
