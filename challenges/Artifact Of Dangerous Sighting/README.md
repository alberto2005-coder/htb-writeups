---
challenge: Artifact Of Dangerous Sighting
type: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, vhdx, ntfs, ads, powershell, evtx]
---

# Artifact Of Dangerous Sighting — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Se entrega una imagen VHDX de Windows. El historial de PowerShell muestra un archivo oculto en un Alternate Data Stream y comandos para borrar logs. Se monta la imagen, se leen los ADS, se recuperan eventos de System.evtx y se desofusca el script para reconstruir la flag.

## Enunciado y superficie

- Forensics, Medium, retirado.
- Imagen `2023-03-09T132449_PANDORA.vhdx`.
- El enunciado indica que el usuario vio abierto el Visor de eventos.

```bash
file 2023-03-09T132449_PANDORA.vhdx
sha256sum 2023-03-09T132449_PANDORA.vhdx
```

## Reconocimiento

```bash
# Montar en solo lectura
sudo mount -o ro,loop,offset=<OFFSET> image.vhdx /mnt/evidence
ls -la /mnt/evidence/Users
```

- La imagen contiene el perfil `Pandora`.
- `ConsoleHost_history.txt` muestra `type finpayload > C:\Windows\Tasks\ActiveSyncProvider.dll:hidden.ps1`.
- Los comandos siguientes borran los logs de PowerShell.

## Análisis del artefacto

El archivo `ActiveSyncProvider.dll` contiene un flujo alternativo llamado `hidden.ps1`. Se lista con `dir /r` o `Get-Item -Stream *` y se extrae con `Get-Content -Stream hidden.ps1`. El script está ofuscado y usa variables y concatenación para ocultar la URL y la flag.

```powershell
Get-Item C:\Windows\Tasks\ActiveSyncProvider.dll -Stream *
Get-Content C:\Windows\Tasks\ActiveSyncProvider.dll -Stream hidden.ps1
```

## Explicación del hallazgo

El atacante usó un ADS para esconder el payload dentro de un DLL legítimo. El historial de PowerShell demuestra la ejecución y el borrado de logs; `System.evtx` conserva parte de la actividad. La desofuscación del script revela la ruta o el valor de la flag.

## Reproducción local

```bash
python3 -m pip install python-evtx
evtx_dump.py /mnt/evidence/Windows/System32/winevt/Logs/System.evtx | grep -i powershell
```

## Evidencia

- Historial de PowerShell con el ADS y `wevtutil cl`.
- Flujo `hidden.ps1` extraído.
- Evento de System.evtx con la ejecución.
- Flag redactada.

## Lecciones aprendidas

- Los ADS son invisibles para un `dir` normal.
- Borrar un log no elimina todos los artefactos.
- El historial de PSReadline es una fuente de alto valor.

## Mitigaciones y detección

- Auditar creación de ADS y ejecución de PowerShell.
- Centralizar logs antes de que el atacante pueda borrarlos.
- Alertar de `wevtutil cl` y `Remove-EventLog`.
- Referencias: MITRE T1564.004, T1070.001, HTB Artifact Of Dangerous Sighting.

## Referencias

- <https://www.hackthebox.com/challenges/Artifact%20Of%20Dangerous%20Sighting>
- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/artifact-of-dangerous-sighting/>
- <https://attack.mitre.org/techniques/T1564/004/>
- <https://attack.mitre.org/techniques/T1070/001/>
