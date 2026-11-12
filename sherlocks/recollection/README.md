---
sherlock: Recollection
difficulty: Easy
category: DFIR
platform: Hack The Box
state: Unverified
tags: [dfir, memory, volatility, windows, powershell, malware]
---

# Recollection — Hack The Box Sherlock

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (04/04/2024). Ficha de referencia; no jugada en este perfil.
> Sin flags, hashes ni cadenas de C2 reales.

## TL;DR

El reto entrega un volcado de memoria de Windows (`recollection.bin`) dentro de `recollection.zip`. Con Volatility 3 se reconstruyen procesos, líneas de comandos, conexiones y memoria inyectada. La actividad maliciosa parte de PowerShell ofuscado que descarga y ejecuta una carga, seguida de inyección en un proceso del sistema. La flag está en la memoria de un proceso o en un fichero recuperado.

## Preparación

```bash
unzip recollection.zip
file recollection.bin
python3 -m venv venv && source venv/bin/activate
pip install volatility3
vol -f recollection.bin windows.info
```

`windows.info` confirma la versión, el build y el esquema de símbolos. Si Volatility no encuentra símbolos, se descargan desde el servidor de Microsoft o se usa el paquete de símbolos incluido en la distribución del Sherlock.

## 1. Procesos

```bash
vol -f recollection.bin windows.pslist
vol -f recollection.bin windows.pstree
vol -f recollection.bin windows.cmdline
```

Qué buscar:

- `powershell.exe` con `-enc`, `-nop`, `-w hidden` o `DownloadString`.
- `rundll32.exe`, `regsvr32.exe`, `mshta.exe` como hijos de Office o del navegador.
- Procesos con nombre legítimo pero ruta en `Temp`, `AppData` o `Downloads`.
- Un `svchost.exe` con PPID que no sea `services.exe`.

```bash
vol -f recollection.bin windows.cmdline | grep -iE 'powershell|rundll32|mshta|regsvr32'
```

## 2. Red

```bash
vol -f recollection.bin windows.netscan
vol -f recollection.bin windows.netstat
```

Se correlacionan PID, IP remota y puerto. Un proceso de usuario con conexión a un puerto 443/8443 externo y sin navegador asociado es sospechoso. Se anota la IP como `<C2_IP>`; no se publica la real.

## 3. Memoria inyectada

```bash
vol -f recollection.bin windows.malfind
vol -f recollection.bin windows.vadinfo --pid <PID>
```

`malfind` marca regiones `PAGE_EXECUTE_READWRITE` sin fichero de respaldo y con cabecera MZ. Se vuelca la región:

```bash
vol -f recollection.bin windows.malfind --dump --pid <PID>
```

Se calcula el hash del volcado y se buscan cadenas:

```bash
strings -a <dump>.dmp | grep -iE 'http|powershell|cmd|flag|HTB'
```

## 4. Ficheros y registro

```bash
vol -f recollection.bin windows.filescan | grep -iE 'temp|download|\.ps1|\.exe'
vol -f recollection.bin windows.dumpfiles --virtaddr <OFFSET>
vol -f recollection.bin windows.registry.hivelist
```

- Se recuperan scripts de PowerShell y ejecutables desde `Temp`.
- `windows.hashdump` puede extraer hashes locales; no se publican.
- `windows.registry.printkey` permite leer Run keys y servicios.

## 5. Línea temporal

| Paso | Evidencia |
|---|---|
| Ejecución inicial | `cmdline` con PowerShell codificado |
| Descarga | `netscan` y cadenas del script |
| Inyección | `malfind` en proceso del sistema |
| Persistencia | Run key o servicio en el registro |
| Flag | Memoria del proceso o fichero volcado |

## Lecciones aprendidas

- En memoria, la línea de comandos vale más que el nombre del proceso.
- `malfind` solo señala regiones sospechosas; la confirmación llega al volcar y mirar cadenas.
- Un `svchost.exe` con conexión externa y PPID raro es una pista fuerte.
- Los scripts en `Temp` suelen contener la URL de descarga y la ruta del payload.
- Hay que normalizar la hora: Volatility trabaja en UTC.

## Mitigaciones y detección

- Registrar PowerShell (4104) y bloquear `-enc` en el dominio salvo excepción.
- Alertar de procesos de usuario con conexiones salientes y de `malfind` en endpoints.
- Usar AMSI y reglas de comportamiento para inyección.
- Detección: PowerShell con `DownloadString`, `rundll32` desde Office, `svchost` con PPID anómalo y regiones RWX.
- Aislar el host y capturar memoria antes de reiniciar.

MITRE: T1059.001, T1105, T1055, T1547.001.

## Referencias

- <https://dev.crollins.io/recollection>
- <https://github.com/volatilityfoundation/volatility3>
- <https://attack.mitre.org/techniques/T1055/>
