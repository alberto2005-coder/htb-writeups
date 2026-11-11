---
sherlock: TickTock
domain: DFIR / Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, mft, teamviewer, powershell, evtx, timestomp, merlin]
---

# TickTock — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired según el writeup público y su etiqueta de dificultad; no comprobado con sesión en HTB.
> Ficha de método; sin respuestas literales, IOCs ni credenciales reales.

## Escenario

Gladys, una empleada nueva, recibe un correo del falso equipo de IT y llama para permitir acceso remoto. El "IT" es un grupo de atacantes. Se entrega un triaje de ~990 ficheros del equipo: MFT, logs de TeamViewer, EVTX, Prefetch, copias de `C:\Windows` y registros de Defender. Hay que reconstruir acceso, ejecución, manipulación del reloj y exfiltración.

## Evidencias

- `$MFT` o su exportación.
- `C/Users/gladys/AppData/Local/TeamViewer/TeamViewer15_Logfile.log`.
- EVTX de PowerShell, Security y System.
- `C/Windows/Prefetch` y `C/Windows/System32` (incluye logs de eventos).
- `C/ProgramData/Microsoft/Windows Defender/Support/MPLog-*.log`.
- Ficheros del escritorio de la usuaria.

```bash
find Collection -maxdepth 3 -type f | wc -l
sha256sum Collection/C/Users/gladys/AppData/Local/TeamViewer/TeamViewer15_Logfile.log
```

## Investigación

### 1. MFT: qué había en el escritorio

```bash
MFTECmd.exe -f 'Collection/C/$MFT' --csv out/ --csvf mft.csv
```

En Timeline Explorer se filtra por `ParentPath` del escritorio de Gladys. Aparecen dos binarios/scripts que no deberían estar ahí: un agente de C2 (`merlin.exe`, agente Go de código abierto) y un script de manipulación de hora (`Invoke-TimeWizard.ps1`). La MFT también da la ruta, el tamaño y los timestamps; si el binario es residente, se puede leer desde el propio registro.

### 2. TeamViewer: acceso y sesión

```bash
grep -iE 'session|connect|start|file|transfer' \
  Collection/C/Users/gladys/AppData/Local/TeamViewer/TeamViewer15_Logfile.log | head -40
```

El log muestra la sesión entrante, el nombre con el que se identificó el atacante, la hora de inicio y la transferencia del agente. Es la prueba del acceso inicial, anterior a cualquier ejecución. La sesión y el nombre se redactan aquí como `<SESSION_ID>` y `<ATTACKER_NAME>`.

### 3. PowerShell y el reloj

```bash
chainsaw search --skip-errors 'powershell' Collection/C/Windows/ \
  --timestamp 'Event.System.TimeCreated_attributes.SystemTime' \
  --from '2023-05-04T11:35:00'
```

Se busca el comando que cambia la hora o configura BitLocker. Los comandos ofuscados en base64 se decodifican con CyberChef o `base64 -d`; el contenido suele incluir la contraseña de BitLocker (`<BITLOCKER_PASS>`) y llamadas a `Set-Date`/`Set-TimeZone`. El script `Invoke-TimeWizard.ps1` confirma la intención.

### 4. Defender y ejecución

```bash
strings -e l 'Collection/C/ProgramData/Microsoft/Windows Defender/Support/MPLog-07102015-052145.log' \
  | grep -i 'merlin.exe'
```

El `MPLog` conserva la categoría asignada al agente y sus hashes (`<SHA1>`/`<SHA256>`), aunque el fichero tenga una fecha antigua: el atacante movió el reloj para que el registro pareciera viejo. La fecha del nombre no es la fecha real de ejecución.

```bash
EvtxECmd.exe -f 'Collection/C/Windows/System32/winevt/Logs/Security.evtx' \
  --csv out/ --csvf security.csv
```

En Security se filtra el evento **4616** (cambio de hora). Hay que separar los cambios hechos por `SystemSettingsAdminFlows.exe` (interfaz de Windows) de los del script; el `SubjectUserSid` y el proceso permiten atribuirlos.

### 5. Línea temporal

| Hora | Fuente | Hecho |
|---|---|---|
| 11:35 | TeamViewer | inicio de la sesión entrante |
| + minutos | MFT | aparición de `merlin.exe` y `Invoke-TimeWizard.ps1` |
| después | PowerShell/EVTX | comandos de hora/BitLocker y ejecución del agente |
| después | Defender | detección/categoría del agente |
| al final | Security 4616 | múltiples cambios de hora atribuibles al script |

La hora de los EVTX y la de la MFT deben interpretarse en UTC; el reloj manipulado afecta a los timestamps del sistema, no a la hora de recepción del SIEM.

## Conclusiones

- El acceso inicial fue **TeamViewer**, no un exploit: ingeniería social con acceso remoto legítimo.
- El atacante dejó un agente C2 y un script de manipulación de hora; el objetivo era dificultar la línea temporal y, probablemente, BitLocker.
- La MFT y el log de TeamViewer prueban la entrega; Defender y los EVTX prueban la ejecución.
- El evento 4616 es la evidencia de la manipulación del reloj, pero hay que separar los cambios legítimos del sistema.
- No se publican la sesión, el nombre, la contraseña, los hashes ni la IP del C2.

## Lecciones

- Un acceso remoto legítimo puede ser el foothold; la telemetría de TeamViewer es tan importante como la de PowerShell.
- La MFT reconstruye la entrega aunque el binario se haya borrado; el nombre y la ruta siguen ahí.
- El base64 no es cifrado: decodificar el comando revela la intención y los secretos.
- Un `MPLog` con fecha antigua puede ser una pista de **timestomping**, no un registro viejo.
- MITRE: T1219 (remote access software), T1059.001 (PowerShell), T1070.006 (timestomp), T1027 (obfuscation), T1562.001 (impair defenses).
- Mitigación: restringir TeamViewer a equipos y usuarios autorizados, habilitar 4616 y script block logging, y correlacionar MFT/EVTX/Defender.

## Referencias

- <https://mwalkowski.com/post/sherlock-ticktock/>
- <https://app.hackthebox.com/sherlocks/TickTock>
