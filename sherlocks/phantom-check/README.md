---
sherlock: Phantom Check
domain: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, powershell, evtx, wmi, anti-vm, nishang, detection]
---

# Phantom Check — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired según el writeup y la ficha de Operation Blackout 2025; no comprobado con sesión en HTB.
> Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Talion sospecha que el atacante hizo comprobaciones **anti-virtualización** para evitar sandboxes. Hay que analizar los logs de PowerShell y reconstruir qué consultas WMI, claves de registro y procesos usó para detectar el entorno.

## Evidencias

```text
Microsoft-Windows-Powershell.evtx
Windows-Powershell-Operational.evtx
```

```bash
sha256sum *.evtx
EvtxECmd.exe -f Microsoft-Windows-Powershell.evtx --csv out/ --csvf powershell.csv
EvtxECmd.exe -f Windows-Powershell-Operational.evtx --csv out/ --csvf ps-operational.csv
```

También se puede usar KAPE con el módulo `EvtxECmd`, o `evtx_dump` para JSONL. Lo importante es conservar el canal y el `Event ID` de cada registro.

## Investigación

### 1. Inventario y canal

Los dos ficheros cubren dos capas distintas:

- **PowerShell/Operational**: eventos 4103 (module logging) y **4104** (script block logging). El 4104 guarda el texto del script, que es donde vive la lógica anti-VM.
- **Windows PowerShell** (classic): eventos 400/800 (engine start/stop) y 600 (provider start). Sirven para ordenar la ejecución, no para leer el script completo.

Se filtran primero los 4104 y se ordenan por tiempo. Un script de reconocimiento de virtualización suele tener una función con varias comprobaciones y una salida por plataforma.

### 2. Consultas WMI

Dentro del script aparecen consultas a:

- **modelo y fabricante** del equipo, para distinguir Hyper-V, VMware, VirtualBox, Xen o QEMU;
- **temperatura** del sistema, una consulta que suele fallar en VM y delata el entorno.

Los nombres exactos que documentan los writeups son `Win32_ComputerSystem` para modelo/fabricante y `MSAcpi_ThermalZoneTemperature` para temperatura. No hace falta ejecutar el script: el 4104 contiene el texto y el evento de error de WMI puede confirmar que la consulta no existe en el host.

```text
Get-WmiObject -Class Win32_ComputerSystem
Get-WmiObject -Query "SELECT * FROM MSAcpi_ThermalZoneTemperature"
```

### 3. Registro y procesos

El script también consulta el registro para buscar servicios de virtualización:

```text
HKLM:\SYSTEM\ControlSet001\Services
```

Y compara nombres de procesos conocidos. En VirtualBox busca `vboxservice.exe` y `vboxtray.exe`; en VMware, `vmwareuser.exe`/`vmwaretray.exe`; en Hyper-V, servicios `vmic*`. La salida del script usa cadenas como `This is a Hyper-V machine` o `This is a VMWare machine`.

La función que engloba todo el reconocimiento es **`Check-VM`**, una adaptación del script de Nishang. Esa firma es el mejor indicador para una regla: no es una consulta aislada, es un bloque que prueba varias plataformas.

### 4. Correlación

- El 4104 da el texto y el `ScriptBlockId`.
- El 4103 da la invocación de cmdlets y parámetros.
- Los eventos clásicos 400/800 dan la hora de arranque y cierre del motor.
- Los errores de WMI (`Invalid class`) confirman que la consulta de temperatura se ejecutó en un host sin ese sensor.

## Conclusiones

- El atacante hizo **environment awareness** antes de ejecutar el payload: comprobó modelo, temperatura, servicios y procesos.
- La lógica está en un script PowerShell (`Check-VM`) y no en un binario, así que el 4104 es la evidencia principal.
- Las consultas WMI y el registro son observables de forma pasiva; no hace falta memoria ni disco.
- La detección debe buscar el patrón completo, no una sola cadena: un script legítimo puede consultar `Win32_ComputerSystem`.

## Lecciones

- **4104 es oro**: sin script block logging, la técnica queda casi invisible.
- Las consultas de temperatura son un buen indicador de anti-VM porque no suelen existir en entornos virtuales.
- El registro `ControlSet001` puede variar (`CurrentControlSet`); la regla debe cubrir ambos.
- Un atacante que comprueba el entorno aún no ha ejecutado el payload; bloquear en ese punto evita el siguiente paso.
- MITRE: T1497.001 (system checks), T1059.001 (PowerShell), T1047 (WMI).
- Mitigación: habilitar PowerShell script block logging y WMI-Activity, enviar los eventos a un SIEM y alertar de `Check-VM`/consultas de temperatura seguidas de ejecución.
